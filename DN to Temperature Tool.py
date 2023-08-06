import os
import cv2
import csv
import tkinter
import numpy as np
import customtkinter
import tkinter as tk
from PIL import Image
import tkinter.messagebox
from tkinter import filedialog
customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue")
#%%
class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app=app
        self.state("normal")
        self.geometry("500x400")
        self.grid_columnconfigure(0, weight=1)
        self.label1 = customtkinter.CTkLabel(self, text="Maximum Temperature",text_color="#F5F0E1",font=customtkinter.CTkFont(size=15,weight="bold"))
        self.label1.grid(row=0,column=0,padx=10, pady=10)
        self.entry1 = customtkinter.CTkEntry(self, placeholder_text="Entry")
        self.entry1.grid(row=1, column=0,padx=(10, 0), pady=(10, 20))
        self.label2 = customtkinter.CTkLabel(self, text="Mimimum Temperature",text_color="#F5F0E1",font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label2.grid(row=2,column=0,padx=10, pady=10)
        self.entry2 = customtkinter.CTkEntry(self, placeholder_text="Entry")
        self.entry2.grid(row=3, column=0, padx=(10, 0), pady=(10, 20))
        
        self.entry_button= customtkinter.CTkButton(self, text="Confirm",command=self.start_processing)
        self.entry_button.grid(row=4, column=0, padx=10, pady=10)
#%%        
    def start_processing(self):
        min_temp = float(self.entry1.get())
        max_temp = float(self.entry2.get())
        
        # Define the mouse callback function
        rect_start = None
        
        inserted_data = []
        # Function to handle mouse events
        def mouse_callback(event, x, y, flags, param):
            global rect_start
            if event == cv2.EVENT_LBUTTONDOWN:
                temperature = min_temp + ((max_temp - min_temp) / (thermal_image1.max() - thermal_image1.min())) * (thermal_image1[y,x] - thermal_image1.min())
                # Draw a circle around the selected point
                cv2.circle(thermal_image, (x, y), 2, (255, 255, 255), -1)
                cv2.putText(thermal_image, "{:.2f}".format(temperature), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                self.app.insert("Temperature at point ({}): {:.2f}".format((x, y), temperature))
                app.update()
                inserted_data.append("Temperature at point ({}): {:.2f}".format((x, y), temperature))
                print(inserted_data)
            if event == cv2.EVENT_RBUTTONDOWN:
                # Start the rectangle drawing process
                rect_start = (x, y)
        
            if event == cv2.EVENT_RBUTTONUP and rect_start:
                # Finish the rectangle drawing process
                x_min, x_max = min(rect_start[0], x), max(rect_start[0], x)
                y_min, y_max = min(rect_start[1], y), max(rect_start[1], y)
                cv2.rectangle(thermal_image, (x_min, y_min), (x_max, y_max), (255, 255, 255), 2)
            
                # Extract the temperature values within the selected region
                rect_temperature = thermal_image2[y_min:y_max, x_min:x_max]
            
                # Add text labels for the temperature values
                max_str = f"Max: {np.max(rect_temperature):.2f} C"
                min_str = f"Min: {np.min(rect_temperature):.2f} C"
                avg_str = f"Avg: {np.mean(rect_temperature):.2f} C"
                cv2.putText(thermal_image, max_str, (x,y_min),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(thermal_image, min_str, (x, y+10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(thermal_image, avg_str, (x_min-40, y+15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                self.app.insert(f"Coordinates:{(x_min, y_min),(x_min, y_min)},{max_str},{min_str},{avg_str}")
                app.update()
                inserted_data.append(f"Coordinates:{(x_min, y_min),(x_min, y_min)},{max_str},{min_str},{avg_str}")
                print(inserted_data)
            cv2.namedWindow('Temperature Image', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Temperature Image', 640, 512)
            cv2.imshow('Temperature Image', thermal_image)
        self.withdraw()    
        # Replace with the actual path to your image
        thermal_image = cv2.imread(file_path)
        
        # Create a color version of the thermal image for visualization
        thermal_image1 = cv2.cvtColor(thermal_image, cv2.COLOR_BGR2GRAY)
        
        # Convert DN (Digital Number) to temperature
        # thermal_range = max_temp - min_temp
        thermal_image2 = min_temp + ((max_temp - min_temp) / (thermal_image1.max() - thermal_image1.min())) * (thermal_image1 - thermal_image1.min())
        
        # Display the temperature image
        cv2.namedWindow('Temperature Image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Temperature Image', 640, 512)
        cv2.imshow('Temperature Image', thermal_image)
        cv2.setMouseCallback('Temperature Image', mouse_callback)
        
        # Wait for key press to exit
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        file_name=file_path.split("/")[-1].split(".")[0]
        # Save the inserted data to a CSV file
        csv_file_path = f"{file_name}_data.csv"
        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for data in inserted_data:
                csv_writer.writerow([data])

        self.deiconify()
#%%
class App(customtkinter.CTk):
    width=1100
    height=580
    def __init__(self):
        super().__init__()

        # configure window
        self.title("DN to Temperature Tool")
        self.geometry(f"{self.width}x{self.height}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path,r"C:\Users\Fuzail Ansari\Downloads\—Pngtree— icon_4697369.png")), size=(20, 20))
        self.home_frame_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="", width=50, command=self.small_sideframe,image=self.image_icon_image)
        self.home_frame_button_1.grid(row=0, column=0, padx=20, pady=10,sticky="w") 
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="MENU", text_color=("white","white"),font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=1, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame,text="Load Image", command=self.load_image)
        self.sidebar_button_1.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame,text="DN to Temperature", command=self.open_toplevel)
        self.sidebar_button_2.grid(row=3, column=0, padx=20, pady=10)
        self.toplevel_window=None
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:",text_color=("white","white"),font=customtkinter.CTkFont(weight="bold"),anchor="w")
        self.scaling_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))     
        
        # load and create background image
        self.bg_image = customtkinter.CTkImage(Image.open(r"C:\Users\Fuzail Ansari\Downloads\paper-style-white-monochrome-background\5605708.jpg"),
                                                size=(2000,1000))
        self.bg_image_label = customtkinter.CTkLabel(self,text="",image= self.bg_image)
        self.bg_image_label.grid(row=0, column=1,rowspan=4)
        
        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=10,width=500, height=300)
        self.home_frame.grid(row=0, column=1, padx=(18, 0), pady=(18, 0))
        
        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, corner_radius=5,width=600,height=200,activate_scrollbars=True)
        self.textbox.grid(row=1, column=1, padx=(18, 0), pady=(18, 0))
#%%        
    def open_toplevel(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it 
            
    def load_image(self):
        global file_path, img
        self.insert("Loading image...")
        file_path = tk.filedialog.askopenfilename(
            title="Select Image",
            filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*"))
        )
        if file_path:
            img = cv2.imread(file_path)
            self.my_image = customtkinter.CTkImage(light_image=Image.open(file_path),
                                      dark_image=Image.open(file_path),
                                      size=(400, 250))
            self.image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.my_image)
            self.image_label.grid(row=0, column=0, padx=20, pady=10)
            self.insert("Image Loaded")     
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
        
    def insert(self,text):
        self.textbox.configure(state="normal")
        self.textbox.insert(tk.END, text + "\n")
        self.textbox.see(tk.END)
        self.textbox.configure(state="disabled")

    def large_sideframe(self):
        self.sidebar_frame.destroy()
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path,r"C:\Users\Fuzail Ansari\Downloads\—Pngtree— icon_4697369.png")), size=(20, 20))
        self.home_frame_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="", width=50, command=self.small_sideframe,image=self.image_icon_image)
        self.home_frame_button_1.grid(row=0, column=0, padx=20, pady=10,sticky="w") 
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="MENU", text_color=("white","white"),font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=1, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame,text="Load Image", command=self.load_image)
        self.sidebar_button_1.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame,text="DN to Temperature", command=self.open_toplevel)
        self.sidebar_button_2.grid(row=3, column=0, padx=20, pady=10)
        self.toplevel_window=None
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:",text_color=("white","white"),font=customtkinter.CTkFont(weight="bold"),anchor="w")
        self.scaling_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

    def small_sideframe(self):
        self.sidebar_frame.destroy()
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=20, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path,r"C:\Users\Fuzail Ansari\Downloads\—Pngtree— icon_4697369.png")), size=(20, 20))
        self.home_frame_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="", width=20, command=self.large_sideframe,image=self.image_icon_image)
        self.home_frame_button_1.grid(row=0, column=0, padx=20, pady=10,sticky="w")  
        
        self.image_icon_image1 = customtkinter.CTkImage(Image.open(os.path.join(image_path,r"C:\Users\Fuzail Ansari\Downloads\pngfind.com-upload-icon-png-661223.png")), size=(20, 20))  
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame,text="", width=20,command=self.load_image,image=self.image_icon_image1)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10,sticky="w")
        self.image_icon_image2 = customtkinter.CTkImage(Image.open(os.path.join(image_path,r"C:\Users\Fuzail Ansari\Downloads\Daco_5635113.png")), size=(20, 20))          
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame,text="", width=20,command=self.open_toplevel,image=self.image_icon_image2)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10,sticky="w")

        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, width=10,values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20),sticky="w")
        self.scaling_optionemenu.set("%")

#%%
if __name__ == "__main__":
    global app
    app = App()
    app.mainloop()
