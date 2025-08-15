import socket as skt
import ssl
import tkinter as tk

#===============================================================================================================================================#
# Parse a URL and make HTTP requests to retrieve the content of the webpage.                                                                    #
#===============================================================================================================================================#

class URL:
    def __init__(self, url):                                                # Parsing a url
        self.scheme, url = url.split("://", 1)                              # Split the URL into scheme and the rest
        assert self.scheme in ("http", "https"), "Invalid URL scheme"       # Confirm that the scheme is either http or https since our browser only supports these

        if self.scheme == "http":                                           # If the scheme is http, set the port to 80
            self.port = 80
        elif self.scheme == "https":                                        # If the scheme is https, set the port to 443
            self.port = 443

        # Separate the host and the path, where the host is the part before the first slash and the path is the rest
        if "/" not in url:
            url += "/"                                                      # Ensure there's a trailing slash if no path is provided

        self.host, url = url.split("/", 1)                                  # Split the URL into host and path
        self.path = "/" + url                                               # Ensure the path starts with a slash

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)                       # If there's a port specified in the host, split it
            self.port = int(port)                                           # Convert the port to an integer

    def request(self):                                                      # Downloading the webpage at the url
        s = skt.socket(family = skt.AF_INET, type = skt.SOCK_STREAM, proto = skt.IPPROTO_TCP)   # Create a TCP socket
        s.connect((self.host, self.port))                                   # Connect to the host on port

        if self.scheme == "https":                                          # If the scheme is https, wrap the socket with SSL
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname = self.host)             # Wrap the socket with SSL for secure communication

        request = "GET {} HTTP/1.0\r\n".format(self.path)                   # Create the HTTP GET request for the path
        request += "Host: {}\r\n".format(self.host)                         # Add the Host header to the request
        request += "\r\n"                                                   # End the request with a blank line to indicate the end of headers
        s.send(request.encode("utf8"))                                      # Send the request to the server

        response = s.makefile("r", encoding = "utf8", newline="\r\n")       # Create a file-like object to read the response
        status_line = response.readline()                                   # Read the first line of the response which contains the status line
        version, status_code, reason = status_line.split(" ", 2)            # Split the status line into version, status code, and reason

        response_headers = {}                                                # Initialize a dictionary to store response headers
        while True:
            line = response.readline()
            if line == "\r\n":                                              # If we reach the end of headers, break the loop
                break

            name, value = line.split(":", 1)                                # Split the header line into name and value
            response_headers[name.casefold()] = value.strip()               # Store the header in the dictionary, stripping whitespace 
            # Convert the header name to lowercase for case-insensitivity

        assert "transfer-encoding" not in response_headers                  # Ensure that chunked transfer encoding is not used
        assert "content-encoding" not in response_headers                   # Ensure that content encoding is not used

        content = response.read()                                           # Read the rest of the response which is the content of the webpage
        s.close()                                                           # Close the socket connection
        return content
    
    def show(self, body):
        in_tag = False
        for c in body:
            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif not in_tag:
                print(c, end="")

    def load(self, url):
        body = url.request()
        self.show(body)

#===============================================================================================================================================#
# Fetch and display content of a URL in a GUI.                                                                                                  #
#===============================================================================================================================================#

WIDTH = 800
HEIGHT = 600

SCROLL_STEP = 100

class Browser:
    def __init__(self):
        self.window = tk.Tk()
        self.frame = tk.Frame(self.window)
        self.frame.pack(fill=tk.BOTH, expand=True)                          # Pack the frame to fill the window and expand with it

        self.canvas = tk.Canvas(self.frame, width=WIDTH, height=HEIGHT)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)           # Pack the canvas to fill the frame and expand with it
        
        self.text = None
        self.display_list = []                                              # Create a list to store the display elements

        #self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Configure>", self.resize)                        # Bind window resize event to the resize function
        
        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)  # Create a vertical scrollbar
        self.scrollbar.pack(side="right", fill="y")                         # Pack the scrollbar to the right side of the window
        self.canvas.config(yscrollcommand=self.scrollbar.set)               # Link the scrollbar to the canvas
        
        self.scroll = 0
        self.window.bind("<MouseWheel>", self.scrolldownup)                 # Bind mouse wheel scroll event to the scrolldown function

    def resize(self, event):                                                # Resize function to adjust the canvas size when the window is resized
        self.canvas.pack()                                                  # Update the canvas size to match the new window size

        WIDTH = self.canvas.winfo_width()

        if self.text is not None:                                           # If there is text loaded, redraw the layout
            self.canvas.delete("all")                                       # Clear the canvas
            new_disp = self.layout(self.text)                               # Redraw the layout when the window is resized
            self.draw(new_disp)                                             # Redraw the display list on the canvas

    def lex(self, body):                                                    # Lexical analysis (modified show function) to extract text from HTML content
        text = ""
        in_tag = False
        for c in body:
            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif not in_tag:
                text += c
        return text
    
    def load(self, url):
        url_object = URL(url)                                               # Create a URL object with the provided URL to be able to parse it using functions defined in the URL class
        body = url_object.request()                                         # Request the content of the URL
        self.text = self.lex(body)                                          # Extract text from the HTML content using the lex function
        display = self.layout(self.text)                                    # Call the layout function to get the display list
        self.draw(display)                                                  # Draw the layout on the canvas

    # Key concepts reviewed in this example code: inheritance, encapsulation, and polymorphism.
    def layout(self, text):
        #self.canvas.create_rectangle(10, 20, 400, 300)
        #self.canvas.create_oval(100, 100, 150, 150)
        #self.canvas.create_text(200, 150, text=f"Loading {url}", font=("Arial", 16))

        global H_Step, V_Step

        self.display_list = []  # Clear previous layout

        H_Step, V_Step = 13, 18
        cursor_x, cursor_y = H_Step, V_Step
        
        #self.window.update_idletasks()                                     # Update the window to ensure the canvas is ready for drawing
        canvas_width = self.canvas.winfo_width()                           # Use actual canvas width
        scrollbar_width = self.scrollbar.winfo_width()
        current_width = canvas_width - scrollbar_width
        
        if current_width < 100:  # Fallback if not yet rendered
            current_width = WIDTH - scrollbar_width

        for c in text:
            self.display_list.append((cursor_x, cursor_y, c))
            cursor_x += H_Step                                              # Allow the print to be able to move to next space to print character so they don't overlap

            if c == "\n":                                                   # If the character is a newline, move to the next line
                cursor_y += V_Step + 1                                      # Additional space added to vertical step when there is a newline char to give illusion of paragraph break
                cursor_x = H_Step                                           # Reset cursor_x to the start of the line
            elif c == " ":                                                  # If the character is a space, move the cursor to the next position
                cursor_x += H_Step                                          # Move the cursor to the next position after a space
            elif cursor_x >= current_width - H_Step:                        # If the cursor reaches the end of the width, move to the next line
                cursor_y += V_Step
                cursor_x = H_Step
        
        return self.display_list                                            # Return the list of display elements to be drawn on the canvas
    
    def draw (self, display_list):
        current_height = self.canvas.winfo_height()                         # Get the current height of the canvas
        
        for x, y, c in display_list:
            if y > self.scroll + current_height: continue                   # If the y position is below the visible area, skip drawing this character
            if y + V_Step < self.scroll: continue                           # If the y position plus the vertical step is above the visible area, skip drawing this character
            self.canvas.create_text(x, y - self.scroll, text=c, font=("Arial", 12))

        bbox = self.canvas.bbox("all")                                      # Get the bounding box of all drawn elements
        if bbox:
            x0, y0, x1, y1 = bbox
            y1 = max(y1, self.canvas.winfo_height())
            self.canvas.config(scrollregion=(x0, y0, x1, y1))               # Update the scroll region of the canvas to encompass all drawn elements
        else:
            self.canvas.config(scrollregion=(0, 0, WIDTH, HEIGHT))          # If no elements are drawn, set the scroll region to the initial size of the canvas
    
    def scrolldownup(self, event):
        if event.delta < 0:                                                 # If scrolling down
            self.scroll += SCROLL_STEP                                      # Increase the scroll value by the scroll step
            self.canvas.delete("all")                                       # Clear the canvas
            self.draw(self.display_list)                                    # Redraw the layout with the updated scroll value
        else:                                                               # If scrolling up
            if self.scroll > 0:                                             # Ensure we don't scroll above the top
                self.scroll -= SCROLL_STEP                                  # Decrease the scroll value by the scroll step
                self.canvas.delete("all")                                   # Clear the canvas
                self.draw(self.display_list)                                # Redraw the layout with the updated scroll value
            else:
                return                                                      # If already at the top, do nothing
    
    
    
