import customtkinter

# TODO allow user to change mode (System, light, dark) or theme (blue, dark-blue, green)
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

app = customtkinter.CTk()
app.geometry("400x240")


def button_function():
    print("button pressed")


button = customtkinter.CTkButton(
    master=app, text="What Wouldn't the Academy Pick?", command=button_function
)
button.place(relx=0.5, rely=0.4, anchor=customtkinter.CENTER)
button = customtkinter.CTkButton(master=app, text="MRCV Game", command=button_function)
button.place(relx=0.5, rely=0.6, anchor=customtkinter.CENTER)

app.mainloop()
