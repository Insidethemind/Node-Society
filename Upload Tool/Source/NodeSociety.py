import sys
import os
import shutil
import time
import requests
from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg
from github import Github, GithubException
import base64

class FormBackgroundWidget(QtWidgets.QWidget):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.fillRect(self.rect(), QtGui.QColor("#131920"))

        svg_background = QtCore.QRectF(0, 0, self.width(), self.height())
        painter.fillRect(svg_background, QtGui.QColor("#0B0E12"))

        if self.svg_renderer.isValid():
            overlay_width = 600 
            available_width = self.width() - overlay_width
            available_height = self.height()

            max_svg_size = min(available_width, available_height) * 0.8  

            svg_left = (available_width - max_svg_size) / 2
            svg_top = (available_height - max_svg_size) / 2


            self.svg_renderer.render(
                painter,
                QtCore.QRectF(svg_left, svg_top, max_svg_size, max_svg_size)
            )
        form_left = self.width() - 500 - 100
        form_rect = QtCore.QRectF(form_left, 0, self.width() - form_left, self.height())
        shadow_offset = -8
        blur_radius = 16
        shadow_rect = form_rect.adjusted(shadow_offset, shadow_offset, shadow_offset, shadow_offset)
        shadow_image = QtGui.QImage(int(shadow_rect.width()) + blur_radius * 2,
                                    int(shadow_rect.height()) + blur_radius * 2,
                                    QtGui.QImage.Format_ARGB32_Premultiplied)
        shadow_image.fill(QtCore.Qt.transparent)
        shadow_painter = QtGui.QPainter(shadow_image)
        shadow_painter.setBrush(QtGui.QColor(0, 0, 0, 150))
        shadow_painter.setPen(QtCore.Qt.NoPen)
        shadow_painter.drawRect(blur_radius, blur_radius,
                                int(shadow_rect.width()), int(shadow_rect.height()))
        shadow_painter.end()
        blurred = QtGui.QImage(shadow_image.size(), QtGui.QImage.Format_ARGB32_Premultiplied)
        blurred.fill(QtCore.Qt.transparent)
        blur_painter = QtGui.QPainter(blurred)
        blur_effect = QtWidgets.QGraphicsBlurEffect()
        blur_effect.setBlurRadius(blur_radius)
        scene = QtWidgets.QGraphicsScene()
        item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(shadow_image))
        scene.addItem(item)
        item.setGraphicsEffect(blur_effect)
        scene.render(blur_painter)
        blur_painter.end()
        painter.drawImage(int(shadow_rect.x()) - blur_radius,
                          int(shadow_rect.y()) - blur_radius, blurred)
        painter.fillRect(form_rect, QtGui.QColor("#1a1a1a"))
        

        version_text = "v1.0.0"
        font = QtGui.QFont("Segoe UI", 9)
        painter.setFont(font)
        painter.setPen(QtGui.QColor("#888"))


        text_rect = painter.boundingRect(QtCore.QRectF(), version_text)
        x = 10  
        y = self.height() - 10  


        y -= text_rect.height()


        painter.drawText(QtCore.QPointF(x, y + text_rect.height()), version_text)


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        svg_path = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), "NodeSociety.svg")
        self.svg_renderer = QtSvg.QSvgRenderer(svg_path)
 
def show_message(parent, title, message, icon=QtWidgets.QMessageBox.Information):
    box = QtWidgets.QMessageBox(parent)
    box.setIcon(icon)
    box.setWindowTitle(title)
    box.setText(f"<span style='color:white;'>{message}</span>")
    box.setStyleSheet("""
        QMessageBox {
            background-color: #1e1e1e;
            color: white;
            font-size: 12pt;
        }
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #7C00D0, stop:1 #FF4161);
            color: white;
            padding: 6px 12px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #5A0098, stop:1 #CC334E);
        }
    """)
    box.exec_()
    


class UploadWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Node Society Project Submission")
        self.setWindowIcon(QtGui.QIcon("NodeSocietyIcon.ico"))
        self.setMinimumSize(1200, 900)   
        self.resize(1200, 900) 

        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        icon_path = os.path.join(base_path, "NodeSocietyIcon.ico")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setGeometry(100, 100, 1000, 850)
        self.setAutoFillBackground(False)
        self.setStyleSheet("""
        QMessageBox {
            background-color: #1e1e1e;
            color: white;
            font-size: 12pt;
        }
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #7C00D0, stop:1 #FF4161);
            color: white;
            padding: 6px 12px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #5A0098, stop:1 #CC334E);
        }
    """)

        svg_path = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), "NodeSociety.svg")
        self.svg_renderer = QtSvg.QSvgRenderer(svg_path)

        form_layout = QtWidgets.QVBoxLayout()
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        button_layout.addStretch()

        button_row = QtWidgets.QHBoxLayout()
        button_row.setAlignment(QtCore.Qt.AlignCenter)

        self.submit_btn = QtWidgets.QPushButton("Submit")
        self.submit_btn.setGraphicsEffect(self.create_shadow_effect())
        self.submit_btn.clicked.connect(self.handle_submission)
        button_row.addWidget(self.submit_btn)

        self.bake_btn = QtWidgets.QPushButton("Bake Metadata Only")
        self.bake_btn.setGraphicsEffect(self.create_shadow_effect())
        self.bake_btn.clicked.connect(self.bake_metadata)
        button_row.addWidget(self.bake_btn)

        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 20)
        button_layout.addStretch()              
        button_layout.addLayout(button_row)     




        title = QtWidgets.QLabel("Project Info")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: white;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        form_layout.addWidget(title)

        def format_label(text):
            return text.replace("*", '<span style="color: red;">*</span>')

        def add_field(label_text, is_password=False, is_multiline=False):
            label = QtWidgets.QLabel()
            label.setTextFormat(QtCore.Qt.RichText)
            label.setText(format_label(label_text))
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("margin-top: 10px; color: white;")
            form_layout.addWidget(label)

            if is_multiline:
                field = QtWidgets.QPlainTextEdit()
            else:
                field = QtWidgets.QLineEdit()
                if is_password:
                    field.setEchoMode(QtWidgets.QLineEdit.Password)

            field.setStyleSheet("background-color: #2e2e2e; color: white; border: none; padding: 6px;")
            form_layout.addWidget(field)
            return field

        self.folder_path = add_field("Project Folder*")

        browse_button = QtWidgets.QPushButton("Browse")
        browse_button.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        browse_button.adjustSize()
        browse_button.clicked.connect(self.browse_folder)

        browse_layout = QtWidgets.QHBoxLayout()
        browse_layout.addStretch()
        browse_layout.addWidget(browse_button)
        browse_layout.addStretch()

        form_layout.addLayout(browse_layout)


        self.project_title = add_field("Project Title*")
        self.description = add_field("Description*", is_multiline=True)
        self.selected_tags = []
        self.tags_display = QtWidgets.QLabel("Selected: None")
        
        version_label = QtWidgets.QLabel()
        version_label.setTextFormat(QtCore.Qt.RichText)
        version_label.setText('<span style="color: red;">*</span> Houdini Version')
        version_label.setAlignment(QtCore.Qt.AlignCenter)
        version_label.setStyleSheet("margin-top: 10px; color: white;")
        form_layout.addWidget(version_label)

        version_layout = QtWidgets.QHBoxLayout()

        self.houdini_version_combo = QtWidgets.QComboBox()
        versions = [f"{v:.1f}" for v in [x * 0.5 for x in range(38, 43)]] 
        self.houdini_version_combo.addItems(versions)
        self.houdini_version_combo.setStyleSheet("background-color: #2e2e2e; color: white; border: none; padding: 6px;")
        version_layout.addWidget(self.houdini_version_combo)

        self.houdini_build_input = QtWidgets.QLineEdit()
        self.houdini_build_input.setPlaceholderText("Optional build (e.g., .563)")
        self.houdini_build_input.setStyleSheet("background-color: #2e2e2e; color: white; border: none; padding: 6px;")
        version_layout.addWidget(self.houdini_build_input)

        form_layout.addLayout(version_layout)




        tag_label = QtWidgets.QLabel("Select Tags")
        tag_label.setAlignment(QtCore.Qt.AlignCenter)  
        tag_label.setStyleSheet("color: white; margin-top: 10px;")
        form_layout.addWidget(tag_label)


        self.tags_display = QtWidgets.QLabel("Selected: None")
        self.tags_display.setWordWrap(True)
        self.tags_display.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.tags_display.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.tags_display.setStyleSheet("""
            color: white;
            padding: 6px;
        """)

        tag_display_layout = QtWidgets.QHBoxLayout()
        tag_display_layout.setContentsMargins(0, 0, 0, 0)
        tag_display_layout.addWidget(self.tags_display)
        form_layout.addLayout(tag_display_layout)


        
        self.select_tags_btn = QtWidgets.QPushButton("Select Tags")
        self.select_tags_btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.select_tags_btn.adjustSize()
        self.select_tags_btn.setStyleSheet("""
            margin-top: 5px;
            padding-left: 25px;
            padding-right: 25px;
        """)
        self.select_tags_btn.clicked.connect(self.open_tag_dialog)



        tag_button_layout = QtWidgets.QHBoxLayout()
        tag_button_layout.addStretch()
        tag_button_layout.addWidget(self.select_tags_btn)
        tag_button_layout.addStretch()
        form_layout.addLayout(tag_button_layout)


        self.github_token = add_field("GitHub Token*", is_password=True)


        self.clear_token_btn = QtWidgets.QPushButton("Clear Saved Token")
        self.clear_token_btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.clear_token_btn.adjustSize()
        self.clear_token_btn.setStyleSheet("padding-left: 25px; padding-right: 25px;")


        clear_token_layout = QtWidgets.QHBoxLayout()
        clear_token_layout.addStretch()
        clear_token_layout.addWidget(self.clear_token_btn)
        clear_token_layout.addStretch()
        form_layout.addLayout(clear_token_layout)


        settings = QtCore.QSettings("NodeSociety", "UploadTool")
        saved_token = settings.value("github_token", "")
        self.github_token.setText(saved_token)
        self.github_token.textChanged.connect(lambda text: settings.setValue("github_token", text))
        self.clear_token_btn.clicked.connect(lambda: [self.github_token.clear(), settings.remove("github_token")])


        self.type_combo = self.create_dropdown("Type*", ["Project Files", "Simulations", "HDAs", "Python Scripts", "Vex Snippets"], form_layout)
        self.skill_combo = self.create_dropdown("Skill Level*", ["Beginner", "Intermediate", "Advanced"], form_layout)
        self.category_combo = self.create_dropdown("Category*", ["SOPs", "DOPs", "CHOPs", "COPs", "TOPs", "Procedural Modeling", "VEX", "VOPs","Solaris or USD", "Materials", "Rendering", "Lighting"], form_layout)
        self.sim_type_combo = self.create_dropdown("Simulation Type*", ["Flip", "POPs", "Vellum", "RBD", "Pyro", "MPM", "FEM", "Other"], form_layout)
        self.sim_type_combo.parent().setVisible(False)


        self.type_combo.currentTextChanged.connect(self.toggle_optional_fields)
        self.toggle_optional_fields(self.type_combo.currentText())


        form_container = QtWidgets.QWidget()
        form_container.setLayout(form_layout)
        form_container.setFixedWidth(500)

        self.button_container = QtWidgets.QWidget()
        self.button_container.setLayout(button_layout)
        self.button_container.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.background_layer = FormBackgroundWidget(self)
        self.background_layer.lower()
        self.background_layer.resize(self.size())

        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(20)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(2, 1)
        grid.addWidget(self.button_container, 0, 1)
        grid.addWidget(form_container, 0, 3)
        grid.addItem(QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum), 0, 4)
        self.setLayout(grid)

        button_style = """
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #7C00D0, stop:1 #FF4161);
                color: white;
                padding: 8px 20px;  /* Increase padding */
                font-size: 10pt;     /* Larger text */
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #6400A8, stop:1 #D13852);
            }
        """

        self.submit_btn.setStyleSheet(button_style)
        self.bake_btn.setStyleSheet(button_style)

        self.submit_btn.raise_()
        self.bake_btn.raise_()

    def toggle_optional_fields(self, value):
        show = value == "Project Files"
        show_simulation_fields = value == "Simulations"
        self.skill_combo.parent().setVisible(show)
        self.category_combo.parent().setVisible(show)
        self.sim_type_combo.parent().setVisible(show_simulation_fields)

    def create_dropdown(self, label_text, options, layout):
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText(label_text.replace("*", '<span style="color: red;">*</span>'))
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("margin-top: 10px; color: white;")
        combo = QtWidgets.QComboBox()
        combo.addItems(options)
        combo.setStyleSheet("background-color: #2e2e2e; color: white; border: none; padding: 6px;")
        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(label)
        container_layout.addWidget(combo)
        layout.addWidget(container)
        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        layout.addItem(spacer)
        combo.container = container
        return combo

    def create_shadow_effect(self):
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QtGui.QColor(0, 0, 0, 160))
        return shadow

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.background_layer.resize(self.size())

    def browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.folder_path.setText(folder)
            
    def open_tag_dialog(self):
        dialog = TagSelectionDialog(current_tags=self.selected_tags, parent=self)
        if dialog.exec_():
            self.selected_tags = dialog.selected
            self.tags_display.setText("Selected: " + ", ".join(self.selected_tags) if self.selected_tags else "None")




    def generate_metadata(self):
        submission_type = self.type_combo.currentText()
        skill = self.skill_combo.currentText() if submission_type == "Project Files" else ""
        category = self.category_combo.currentText() if submission_type == "Project Files" else ""
        sim_type = self.sim_type_combo.currentText() if submission_type == "Simulations" else ""

        base_version = self.houdini_version_combo.currentText()
        build = self.houdini_build_input.text().strip()
        if build:
            if not build.startswith("."):
                build = f".{build}"
            houdini_version = f"{base_version}{build}"
        else:
            houdini_version = base_version

        metadata = f"""
Title: {self.project_title.text()}
Description: {self.description.toPlainText()}
Houdini Version: {houdini_version}
Tags: {", ".join(self.selected_tags)}
Author: {self.get_github_username(self.github_token.text())}
Type: {submission_type}
Skill Level: {skill}
Category: {category}
Simulation Type: {sim_type}
""".strip()

        return metadata



    def bake_metadata(self):
        if not self.folder_path.text().strip() or not self.project_title.text().strip() or not self.description.toPlainText().strip() or not self.houdini_version_combo.currentText().strip() or not self.github_token.text().strip():
            show_message(self, "Missing Fields", "Please fill in all required (*) fields before baking metadata.", QtWidgets.QMessageBox.Warning)
            return

        folder = self.folder_path.text()
        try:
            with open(os.path.join(folder, "metadata.txt"), "w", encoding="utf-8") as f:
                f.write(self.generate_metadata())
            show_message(self, "Done", "Metadata baked successfully!", QtWidgets.QMessageBox.Information)
        except Exception as e:
            show_message(self, "Error", f"Failed to write metadata: {e}", QtWidgets.QMessageBox.Critical)


    def get_github_username(self, token):
        try:
            response = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"})
            return response.json().get("login", "Unknown") if response.status_code == 200 else "Unknown"
        except:
            return "Unknown"

    def handle_submission(self):
        if not all([
            self.folder_path.text().strip(),
            self.project_title.text().strip(),
            self.description.toPlainText().strip(),
            self.houdini_version_combo.currentText().strip(),
            self.github_token.text().strip()
        ]): 
            show_message(self, "Missing Fields", "Please fill in all required (*) fields before submitting.", QtWidgets.QMessageBox.Warning)
            return

        token = self.github_token.text().strip()
        g = Github(token)
        user = g.get_user()
        username = user.login
        repo_name = "Node-Society"

        try:
            upstream_repo = g.get_repo(f"Insidethemind/{repo_name}")

            try:
                fork = g.get_repo(f"{username}/{repo_name}")
            except:
                fork = user.create_fork(upstream_repo)
                for _ in range(20):
                    try:
                        fork = g.get_repo(f"{username}/{repo_name}")
                        break
                    except:
                        time.sleep(2)
                else:
                    show_message(self, "Timeout", "Fork did not become available in time.", QtWidgets.QMessageBox.Critical)
                    return


            try:
                upstream_branch = upstream_repo.get_branch("main")
                fork.get_git_ref("heads/main").edit(upstream_branch.commit.sha, force=True)
            except Exception as sync_error:
                show_message(self, "Sync Failed", f"Could not sync fork with upstream.\n{sync_error}", QtWidgets.QMessageBox.Critical)
                return

            pulls = upstream_repo.get_pulls(state='open', head=f"{username}:main")
            if pulls.totalCount > 0:
                show_message(
                    self,
                    "Pull Request Exists",
                    f"<span style='color:white;'>A pull request already exists: <a href='{pulls[0].html_url}'>{pulls[0].html_url}</a></span>",
                    QtWidgets.QMessageBox.Warning
                )
                return

            local_folder = self.folder_path.text().strip()

            submission_type = self.type_combo.currentText()
            project_title = self.project_title.text()

            if submission_type == "Project Files":
                base_path = f"{submission_type}/{self.skill_combo.currentText()}/{self.category_combo.currentText()}/{project_title}"
            elif submission_type == "Simulations":
                base_path = f"{submission_type}/{self.sim_type_combo.currentText()}/{project_title}"
            else:
                base_path = f"{submission_type}/{project_title}"

            try:
                existing_contents = upstream_repo.get_contents(base_path)
                existing_metadata = [item for item in existing_contents if item.name == "metadata.txt"]

                if existing_metadata:
                    metadata_file = existing_metadata[0]
                    metadata_content = base64.b64decode(metadata_file.content).decode("utf-8", errors="ignore")
                    if f"Author: {username}" not in metadata_content:
                        show_message(
                            self,
                            "Project Exists",
                            "A project with this name already exists and you are not the original author. Please rename your project.",
                            QtWidgets.QMessageBox.Warning
                        )
                        return
                    else:
                        msg_box = QtWidgets.QMessageBox(self)
                        msg_box.setIcon(QtWidgets.QMessageBox.Question)
                        msg_box.setWindowTitle("Update Project")
                        msg_box.setText("<span style='color:white;'>You are the author of this project. Do you want to update it?</span>")
                        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                        msg_box.setStyleSheet("""
                            QMessageBox {
                                background-color: #1e1e1e;
                                color: white;
                                font-size: 12pt;
                            }
                            QPushButton {
                                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #3CB8FF, stop:1 #0025FF);
                                color: white;
                                padding: 6px 12px;
                                border-radius: 8px;
                            }
                            QPushButton:hover {
                                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #2DAAE0, stop:1 #001FCC);
                            }
                        """)
                        result = msg_box.exec_()
                        if result != QtWidgets.QMessageBox.Yes:
                            return
            except GithubException as ge:
                if ge.status != 404:
                    raise

            metadata_content = self.generate_metadata()
            metadata_path = os.path.join(local_folder, "metadata.txt")
            with open(metadata_path, "w", encoding="utf-8") as f:
                f.write(metadata_content)

            uploaded_files = os.listdir(local_folder)

            for file in uploaded_files:
                path = f"{base_path}/{file}"
                file_path = os.path.join(local_folder, file)

                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        encoding = "text"
                    except UnicodeDecodeError:
                        with open(file_path, "rb") as f:
                            content = f.read()
                        encoding = "binary"

                    try:
                        existing = fork.get_contents(path)
                        sha = existing.sha
                        fork.update_file(
                            path=path,
                            message=f"Update {file}",
                            content=content,
                            sha=sha
                        )
                    except GithubException as ge:
                        if ge.status == 404:
                            fork.create_file(
                                path=path,
                                message=f"Add {file}",
                                content=content
                            )
                        else:
                            raise



            pr = upstream_repo.create_pull(
                title=f"New Submission: {self.project_title.text()}",
                body="Submitted via Node Society Upload tool.",
                head=f"{username}:main",
                base="main"
            )


            show_message(
                self,
                "Success",
                f"<span style='color:white;'>Submitted pull request: <a href='{pr.html_url}'>{pr.html_url}</a></span>",
                QtWidgets.QMessageBox.Information
            )

        except Exception as e:
            show_message(self, "Pull Request Error", f"<span style='color:white;'>Failed to create pull request: {e}</span>", QtWidgets.QMessageBox.Critical)

class TagSelectionDialog(QtWidgets.QDialog):
    def __init__(self, current_tags=None, max_tags=6, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Tags")
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: white;
                font-size: 12pt;
            }
        """)

        self.selected = set(current_tags or [])
        self.max_tags = max_tags
        self.tag_buttons = {}

        layout = QtWidgets.QVBoxLayout(self)

        tag_sections = {
            "Contexts": ["SOPs", "DOPs", "LOPs", "ROPs", "CHOPs", "COPs", "TOPs", "MATs"],
            "Rendering Engines": ["Karma", "Mantra", "Redshift", "Arnold", "Octane", "Vray"],
            "Simulation Types": ["Pyro", "Flip", "RBD", "MPM", "Vellum", "Crowds", "POPs"],
            "General": ["Procedural Modeling", "Heightfields", "Materials", "Lighting", "Compositing", "Simulation", "Rendering", "USD", "HDA", "Solaris"],
            "Scripting": ["VEX", "VOPs", "Python"],
            "Skill Level": ["Beginner", "Intermediate", "Advanced"]
        }

        for section, tags in tag_sections.items():
            group_box = QtWidgets.QGroupBox(section)
            group_box.setStyleSheet("QGroupBox { color: white; font-weight: bold; }")
            group_layout = QtWidgets.QGridLayout()
            group_layout.setHorizontalSpacing(8)
            group_layout.setVerticalSpacing(8)

            for i, tag in enumerate(tags):
                btn = QtWidgets.QPushButton(tag)
                btn.setCheckable(True)
                btn.setChecked(tag in self.selected)
                btn.setStyleSheet("""
                    QPushButton {
                        border: 2px solid #7C00D0;
                        border-radius: 16px;
                        padding: 4px 12px;
                        background-color: transparent;
                        color: white;
                    }
                    QPushButton:checked {
                        background-color: #7C00D0;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #3a0b55;
                    }
                """)
                btn.clicked.connect(self.toggle_tag)
                self.tag_buttons[tag] = btn
                row = i // 4  
                col = i % 4
                group_layout.addWidget(btn, row, col)

            group_box.setLayout(group_layout)
            layout.addWidget(group_box)

        layout.addStretch()

        button_row = QtWidgets.QHBoxLayout()
        button_row.setAlignment(QtCore.Qt.AlignCenter)

        clear_btn = QtWidgets.QPushButton("Clear Tags")
        clear_btn.clicked.connect(self.clear_tags)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #7C00D0, stop:1 #FF4161);
                color: white;
                padding: 6px 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #5A0098, stop:1 #CC334E);
            }
        """)

        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.clicked.connect(self.accept_selection)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #7C00D0, stop:1 #FF4161);
                color: white;
                padding: 6px 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #5A0098, stop:1 #CC334E);
            }
        """)

        button_row.addWidget(clear_btn)
        button_row.addSpacing(10)
        button_row.addWidget(ok_btn)
        layout.addLayout(button_row)

    def toggle_tag(self):
        sender = self.sender()
        tag = sender.text()
        if sender.isChecked():
            if len(self.selected) >= self.max_tags:
                sender.setChecked(False)
                show_message(
                    self,
                    "Limit Exceeded",
                    f"You can select up to {self.max_tags} tags.",
                    QtWidgets.QMessageBox.Warning
                )
            else:
                self.selected.add(tag)
        else:
            self.selected.discard(tag)

    def clear_tags(self):
        for tag, btn in self.tag_buttons.items():
            btn.setChecked(False)
        self.selected.clear()

    def accept_selection(self):
        self.selected = list(self.selected)
        if not self.selected:
            self.selected = []
        self.accept()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("NodeSociety.ico"))
    window = UploadWindow()
    window.show()
    sys.exit(app.exec_())