from enum import Enum

class DepthFilter(Enum):
    Left = 0
    Right = 1
    Up = 2
    Down = 3
    Front = 4
    Back = 5
    Rotation = 6

class LogColor(Enum):
    Red = 0
    Yellow =1
    White = 2
    Black = 3
    Orange =4
    Green =5
    Gray = 6
    BackGround = 7