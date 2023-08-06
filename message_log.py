from typing import Reversible
import textwrap

import tcod

import color



class Message:
    def __init__(self, text: str, fg: tuple[int, int, int]) -> None:
        self.plain_text = text
        self.fg = fg
        self.count = 1
    
    @property
    def full_text(self) -> str:
        """The full text of the message, including the count if necessary"""
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text


class MessageLog:
    def __init__(self) -> None:
        self.messages: list[Message] = []
    
    def add_message(
        self, text:str, fg: tuple[int, int, int] = color.white, *, stack: bool = True,
    ) -> None:
        """Add a message to this log

        Args:
            text (str): Message to add to log
            fg (color, optional): Text Color. Defaults to color.white.
            stack (bool, optional): if True,
            the message can stack wiht a previous message of the same text. Defaults to True.
        """
        
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text,fg))
    
    def render(
        self, console: tcod.console.Console, x: int, y: int, width:int, height:int,
    ) -> None: 
        """Render this log over the given area.

        Args:
            console (tcod.console.Console): Console to render onto
            x (int): x position of log
            y (int): y position of long
            width (int): width of log
            height (int): height of log
        """
        
        self.render_messages(console, x,y, width, height, self.messages)
    
    @staticmethod
    def render_messages(
        console: tcod.console.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message]
    ) -> None:
        """Render the messages provided

        Args:
            console (tcod.console.Console): Console to be rendered onto
            x (int): x position of message
            y (int): y position of message
            width (int): width of message
            height (int): height of message
            messages (Reversible[Message]): list of messages to render
        """
        
        y_offset = height - 1
        
        for message in reversed(messages):
            for line in reversed(textwrap.wrap(message.full_text, width)):
                console.print(x=x, y=y+y_offset, string=line, fg=message.fg)
                y_offset -= 1
                if y_offset < 0:
                    return