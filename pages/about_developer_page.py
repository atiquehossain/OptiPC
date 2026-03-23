from __future__ import annotations

import customtkinter as ctk
import webbrowser

from pages.base_page import BasePage


class AboutDeveloperPage(BasePage):
    def __init__(self, parent, logger, status_service, system_service, action_service) -> None:
        super().__init__(parent, logger, status_service, system_service, action_service)

    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure(0, weight=1)

        # Header Card
        header = self.make_card(wrapper, "About the Developer", "Meet the creator of OptiPC")
        header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Developer Info
        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            info_frame, 
            text="Atique Hossain", 
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", pady=(0, 8))
        
        ctk.CTkLabel(
            info_frame, 
            text="Windows System Optimization Expert", 
            text_color="gray70",
            font=ctk.CTkFont(size=16)
        ).pack(anchor="w", pady=(0, 16))
        
        ctk.CTkLabel(
            info_frame,
            text="I'm a passionate Windows system optimization specialist with expertise in creating user-friendly tools that make computer maintenance accessible to everyone. OptiPC is my flagship project designed to help users keep their Windows systems running smoothly with professional-grade tools wrapped in an intuitive interface.",
            justify="left",
            wraplength=600,
            text_color="gray60",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 20))

        # Mission Section
        mission = self.make_card(wrapper, "My Mission", "What drives me to create OptiPC")
        mission.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        mission_points = [
            "🎯 Democratize Windows system maintenance",
            "🛠️ Create powerful yet simple-to-use tools", 
            "🌐 Provide free, open-source solutions",
            "⚡ Help users optimize their PC performance"
        ]

        for point in mission_points:
            ctk.CTkLabel(
                mission,
                text=point,
                font=ctk.CTkFont(size=14),
                anchor="w"
            ).pack(anchor="w", padx=20, pady=(8, 4))

        # Connect Section
        connect = self.make_card(wrapper, "Connect With Me", "Get in touch or follow my work")
        connect.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        links = ctk.CTkFrame(connect, fg_color="transparent")
        links.pack(fill="x", padx=20, pady=20)
        links.grid_columnconfigure((0, 1), weight=1)

        # Left column links
        left_col = ctk.CTkFrame(links, fg_color="transparent")
        left_col.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self._make_link_button(left_col, "🔗 LinkedIn", "https://www.linkedin.com/in/atique-hossain/", "Professional profile and connections").pack(fill="x", pady=(0, 8))
        self._make_link_button(left_col, "💻 GitHub", "https://github.com/atiquehossain", "Open source projects and code").pack(fill="x", pady=(0, 8))
        self._make_link_button(left_col, "🌐 Website", "https://atiquehossain.github.io/", "Personal portfolio and projects").pack(fill="x", pady=(0, 8))

        # Right column links
        right_col = ctk.CTkFrame(links, fg_color="transparent")
        right_col.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        self._make_link_button(right_col, "📷 Instagram", "https://www.instagram.com/imatiquehossain/", "Follow my journey").pack(fill="x", pady=(0, 8))
        self._make_link_button(right_col, "🏢 IT Services", "https://nexgenscript.com/", "Professional IT solutions").pack(fill="x", pady=(0, 8))

        # Skills Section
        skills = self.make_card(wrapper, "Technical Expertise", "Technologies I work with")
        skills.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        skill_areas = [
            ("🪟 Windows System Administration", "Deep knowledge of Windows internals, optimization, and troubleshooting"),
            ("🐍 Python Development", "CustomTkinter, system monitoring, automation tools"),
            ("💾 Database Management", "Performance optimization and data analysis"),
            ("🔧 System Integration", "API development and third-party service integration"),
            ("🛡️ Security & Performance", "System hardening and performance tuning")
        ]

        for skill, description in skill_areas:
            skill_frame = ctk.CTkFrame(skills, fg_color="transparent")
            skill_frame.pack(fill="x", padx=20, pady=(12, 8))
            
            ctk.CTkLabel(
                skill_frame,
                text=skill,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            ).pack(anchor="w", pady=(0, 4))
            
            ctk.CTkLabel(
                skill_frame,
                text=description,
                text_color="gray60",
                font=ctk.CTkFont(size=12),
                wraplength=500,
                justify="left"
            ).pack(anchor="w", pady=(0, 0))

        self.status_service.info("About Developer page loaded", toast=False)

    def _make_link_button(self, parent, text: str, url: str, description: str = "") -> None:
        """Create a styled link button"""
        button = ctk.CTkButton(
            parent,
            text=text,
            command=lambda: webbrowser.open(url),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40,
            corner_radius=8
        )
        if description:
            tooltip = ctk.CTkLabel(parent, text=description, text_color="gray50", font=ctk.CTkFont(size=11))
            # Simple tooltip implementation
            def on_enter(e):
                tooltip.place(x=button.winfo_x() + button.winfo_width() + 10, y=button.winfo_y())
            
            def on_leave(e):
                tooltip.place_forget()
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        
        return button
