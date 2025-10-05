class Theme:
    #Управление темами оформления"

    def __init__(self):
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                "bg": "#2f3136", "bg_secondary": "#36393f", "bg_tertiary": "#40444b",
                "fg": "#ffffff", "fg_secondary": "#b9bbbe", "accent": "#007bff",
                "accent_hover": "#0056b3", "entry_bg": "#40444b", "entry_fg": "#ffffff",
                "listbox_bg": "#40444b", "listbox_fg": "#ffffff", "text_bg": "#40444b",
                "text_fg": "#ffffff", "button_bg": "#007bff", "button_fg": "#ffffff",
                "status_bg": "#36393f", "status_fg": "#b9bbbe", "scrollbar_bg": "#007bff",
                "scrollbar_trough": "#40444b", "scrollbar_active": "#0056b3",
                "cursor_color": "#ffffff"
            },
            "light": {
                "bg": "#f8f9fa", "bg_secondary": "#ffffff", "bg_tertiary": "#e9ecef",
                "fg": "#212529", "fg_secondary": "#6c757d", "accent": "#007bff",
                "accent_hover": "#0056b3", "entry_bg": "#ffffff", "entry_fg": "#212529",
                "listbox_bg": "#ffffff", "listbox_fg": "#212529", "text_bg": "#ffffff",
                "text_fg": "#212529", "button_bg": "#007bff", "button_fg": "#ffffff",
                "status_bg": "#e9ecef", "status_fg": "#6c757d", "scrollbar_bg": "#007bff",
                "scrollbar_trough": "#e9ecef", "scrollbar_active": "#0056b3",
                "cursor_color": "#212529"
            }
        }

    def get_theme(self):
        return self.themes[self.current_theme]

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"

        return self.get_theme()
