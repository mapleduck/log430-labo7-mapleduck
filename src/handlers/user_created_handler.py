"""
Handler: User Created
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import os
from pathlib import Path
from handlers.base import EventHandler
from typing import Dict, Any


class UserCreatedHandler(EventHandler):
    """Handles UserCreated events"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        super().__init__()
    
    def get_event_type(self) -> str:
        """Return the event type this handler processes"""
        return "UserCreated"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        user_id = event_data.get('id')
        name = event_data.get('name')
        email = event_data.get('email')
        datetime = event_data.get('datetime')
        user_type_id = event_data.get('user_type_id', 1)

        current_file = Path(__file__)
        project_root = current_file.parent.parent

        # 1 = Client, 2 = Employee, 3 = Manager
        if user_type_id == 1:
            template = "welcome_client_template.html"
            message = "Merci d'avoir visité notre magasin. Si vous avez des questions, n'hésitez pas à nous contacter."
        else:
            template = "welcome_client_template.html"
            message = "Salut et bienvenue dans l'équipe ! Nous sommes ravis de t'avoir parmi nous."

        with open(project_root / "templates" / template, 'r') as file:
            html_content = file.read()

        html_content = html_content.replace("{{user_id}}", str(user_id))
        html_content = html_content.replace("{{name}}", name)
        html_content = html_content.replace("{{email}}", email)
        html_content = html_content.replace("{{creation_date}}", datetime)
        html_content = html_content.replace(
            "Merci d'avoir visité notre magazin. Si vous avez des questions ou des problèmes concernant votre achat, n'hésitez pas à nous contacter.",
            message
        )

        filename = os.path.join(self.output_dir, f"welcome_{user_id}.html")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.debug(f"Courriel HTML généré à {name} (ID: {user_id}), {filename}")