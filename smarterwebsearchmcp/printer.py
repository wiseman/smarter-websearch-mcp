from rich.console import Console

class Printer:
    def __init__(self, console: Console | None = None):
        self.console = console if console else Console()
        self.items = {}

    def update_item(self, key: str, message: str, is_done: bool = False, hide_checkmark: bool = False):
        self.items[key] = {"message": message, "is_done": is_done}
        status = "[green]✔[/green]" if is_done and not hide_checkmark else "[blue]⏳[/blue]"
        self.console.print(f"{status} {key}: {message}")

    def mark_item_done(self, key: str):
        if key in self.items:
            self.items[key]["is_done"] = True
            message = self.items[key]["message"]
            self.console.print(f"[green]✔[/green] {key}: {message}")
        else:
            self.console.print(f"[yellow]Warning:[/yellow] Tried to mark unknown item '{key}' as done.")

    def end(self):
        self.console.print("[bold green]All operations complete.[/bold green]")
