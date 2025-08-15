import sys
import browser_h as b
import tkinter as tk
    
if __name__ == "__main__":
    # website = b.URL()
    # website.load(sys.argv[1])         # Previous implementation to load URL directly without GUI

    browser = b.Browser()
    browser.load((sys.argv[1]))
    tk.mainloop()