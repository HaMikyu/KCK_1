import sys
import pandas as pd
from PIL import Image
from rich.syntax import Syntax
from rich.traceback import Traceback
from rich.table import Table
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive, var
from textual.widgets import DirectoryTree, Footer, Header, Static

ASCII = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']

class CodeBrowser(App):
    """Textual code browser app."""
    theme = reactive("github-dark")
    CSS_PATH = "code_browser.tcss"
    BINDINGS = [
        ("f", "toggle_files", "Toggle Files"),
        ("q", "quit", "Quit"),
    ]

    theme = reactive("github-dark")

    show_tree = var(True)
    path: reactive[str | None] = reactive(None)

    def __init__(self,path2):
        super().__init__()
        self.path3 = path2

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        """Compose our UI."""

        path=self.path3
        #path = "./" if len(sys.argv) < 2 else sys.argv[1]
        yield Header()
        with Container():
            yield DirectoryTree(path, id="tree-view")
            with VerticalScroll(id="code-view"):
                yield Static(id="code", expand=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user clicks a file in the directory tree."""
        event.stop()
        self.path = str(event.path)

    def watch_path(self, path: str | None) -> None:
        """Called when path changes."""
        code_view = self.query_one("#code", Static)
        if path is None:
            code_view.update("")
            return

        try:
            if path.endswith(".xlsx") or path.endswith(".csv"):
                table = self.render_excel_as_table(path)
                code_view.update(table)
            elif path.endswith('.png') or path.endswith('.jpeg') or path.endswith('.jpg'):
                ascii_art = self.convert_image_to_ascii(path)
                code_view.update(ascii_art)
            else:
                syntax = Syntax.from_path(
                    path,
                    line_numbers=True,
                    word_wrap=False,
                    indent_guides=True,
                    theme=self.theme
                )
                code_view.update(syntax)
                self.query_one("#code-view").scroll_home(animate=False)
                self.sub_title = path
        except Exception:
            code_view.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"

    def render_excel_as_table(self, path):
        df = pd.read_excel(path)
        table = Table(title="Excel Data", show_lines=True)

        for column in df.columns:
            table.add_column(column)

        for index, row in df.iterrows():
            row_values = [str(value) for value in row]
            table.add_row(*row_values)

        return table

    def convert_image_to_ascii(self,image_path, new_width= 100):
        try:
            img = Image.open(image_path).convert('L')
            width, height = img.size
            ratio = height / width
            new_height = int(ratio * new_width*0.55)
            img = img.resize((new_width, new_height))
            pixels = img.getdata()
            ascii_str = ""
            for pixel in pixels:
                ascii_str += ASCII[pixel // 25] #sprytne
            result = ""
            for i in range(0, len(ascii_str), new_width):
                result += ascii_str[i:i + new_width] + "\n"

            return result
        except Exception as e:
            return f"Error while making ascii art: {e}"

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree


if __name__ == "__main__":
    CodeBrowser("./ruchy/").run()
