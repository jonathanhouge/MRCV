import customtkinter
from PIL import Image, ImageTk

customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme(
    "blue"
)  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.geometry("400x240")


def button_function():
    print("button pressed")


# Use CTkButton instead of tkinter Button
button = customtkinter.CTkButton(master=app, text="CTkButton", command=button_function)
button.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

button_image = customtkinter.CTkImage(
    Image.open("research/raising_arizona.jpg"), size=(100, 150)
)

image_button = customtkinter.CTkButton(
    master=app,
    image=button_image,
)
image_button.pack()

app.mainloop()
