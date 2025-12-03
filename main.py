import math
import datetime
from enum import Enum
from typing import List, Union
from contextlib import redirect_stdout
import os


class Color(Enum):
    RED = "красный"
    ORANGE = "оранжевый" 
    YELLOW = "желтый"
    GREEN = "зеленый"
    CYAN = "голубой"
    BLUE = "синий"
    VIOLET = "фиолетовый"


class Shape:
    def __init__(self, color: Color):
        self.color = color
        self.last_edit_date = datetime.datetime.now()
    
    def get_area(self) -> float:
        raise NotImplementedError("Метод должен быть реализован в подклассе")
    
    def get_perimeter(self) -> float:
        raise NotImplementedError("Метод должен быть реализован в подклассе")
    
    def __str__(self) -> str:
        raise NotImplementedError("Метод должен быть реализован в подклассе")
    
    def update_edit_date(self):
        self.last_edit_date = datetime.datetime.now()


class Circle(Shape):
    def __init__(self, center_x: int, center_y: int, radius: int, color: Color):
        super().__init__(color)
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
    
    def get_area(self) -> float:
        return math.pi * self.radius ** 2
    
    def get_perimeter(self) -> float:
        return 2 * math.pi * self.radius
    
    def __str__(self) -> str:
        return (f"Круг: центр({self.center_x},{self.center_y}), "
                f"радиус={self.radius}, цвет={self.color.value}, "
                f"площадь={self.get_area():.2f}, периметр={self.get_perimeter():.2f}, "
                f"дата редактирования: {self.last_edit_date.strftime('%Y-%m-%d %H:%M:%S')}")


class Rectangle(Shape):
    def __init__(self, top_left_x: float, top_left_y: float, 
                 bottom_right_x: float, bottom_right_y: float, color: Color):
        super().__init__(color)
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.bottom_right_x = bottom_right_x
        self.bottom_right_y = bottom_right_y
    
    def get_width(self) -> float:
        return abs(self.bottom_right_x - self.top_left_x)
    
    def get_height(self) -> float:
        return abs(self.bottom_right_y - self.top_left_y)
    
    def get_area(self) -> float:
        return self.get_width() * self.get_height()
    
    def get_perimeter(self) -> float:
        return 2 * (self.get_width() + self.get_height())
    
    def __str__(self) -> str:
        return (f"Прямоугольник: верхний левый({self.top_left_x},{self.top_left_y}), "
                f"нижний правый({self.bottom_right_x},{self.bottom_right_y}), "
                f"цвет={self.color.value}, площадь={self.get_area():.2f}, "
                f"периметр={self.get_perimeter():.2f}, "
                f"дата редактирования: {self.last_edit_date.strftime('%Y-%m-%d %H:%M:%S')}")


class Triangle(Shape):
    def __init__(self, x1: float, y1: float, x2: float, y2: float, 
                 x3: float, y3: float, color: Color):
        super().__init__(color)
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.x3, self.y3 = x3, y3
    
    def get_area(self) -> float:
        return abs((self.x1*(self.y2-self.y3) + 
                   self.x2*(self.y3-self.y1) + 
                   self.x3*(self.y1-self.y2)) / 2.0)
    
    def get_perimeter(self) -> float:
        side1 = math.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)
        side2 = math.sqrt((self.x3 - self.x2)**2 + (self.y3 - self.y2)**2)
        side3 = math.sqrt((self.x1 - self.x3)**2 + (self.y1 - self.y3)**2)
        return side1 + side2 + side3
    
    def __str__(self) -> str:
        return (f"Треугольник: точки({self.x1},{self.y1}), "
                f"({self.x2},{self.y2}), ({self.x3},{self.y3}), "
                f"цвет={self.color.value}, площадь={self.get_area():.2f}, "
                f"периметр={self.get_perimeter():.2f}, "
                f"дата редактирования: {self.last_edit_date.strftime('%Y-%m-%d %H:%M:%S')}")


class CommandParser:
    def __init__(self):
        self.shapes: List[Shape] = []
    
    def parse_color(self, color_str: str) -> Color:
        color_map = {
            "красный": Color.RED,
            "оранжевый": Color.ORANGE,
            "желтый": Color.YELLOW,
            "зеленый": Color.GREEN,
            "голубой": Color.CYAN,
            "синий": Color.BLUE,
            "фиолетовый": Color.VIOLET
        }
        return color_map.get(color_str, Color.RED)
    
    def parse_add_command(self, data: str) -> Union[Shape, None]:
        parts = data.split()
        if not parts:
            return None
        
        shape_type = parts[0]
        
        if shape_type == "CIRCLE":
            x, y, r = int(parts[1]), int(parts[2]), int(parts[3])
            color = self.parse_color(parts[4])
            return Circle(x, y, r, color)
        
        elif shape_type == "RECTANGLE":
            tl_x, tl_y = float(parts[1]), float(parts[2])
            br_x, br_y = float(parts[3]), float(parts[4])
            color = self.parse_color(parts[5])
            return Rectangle(tl_x, tl_y, br_x, br_y, color)
        
        elif shape_type == "TRIANGLE":
            x1, y1 = float(parts[1]), float(parts[2])
            x2, y2 = float(parts[3]), float(parts[4])
            x3, y3 = float(parts[5]), float(parts[6])
            color = self.parse_color(parts[7])
            return Triangle(x1, y1, x2, y2, x3, y3, color)
        
        return None
    
    def matches_condition(self, shape: Shape, condition: str) -> bool:
        parts = condition.split()
        if len(parts) < 3:
            return False
        
        field, op, value_str = parts[0], parts[1], parts[2]
        
        try:
            value = float(value_str)
        except ValueError:
            return False
        
        if field == "area":
            area = round(shape.get_area(), 2)
            value = round(value, 2)

            if op == ">": return area > value
            if op == "<": return area < value
            if op == ">=": return area >= value
            if op == "<=": return area <= value
            if op == "==": return abs(area - value) < 0.001
        
        elif field == "perimeter":
            perimeter = round(shape.get_perimeter(), 2)
            value = round(value, 2)

            if op == ">": return perimeter > value
            if op == "<": return perimeter < value
            if op == ">=": return perimeter >= value
            if op == "<=": return perimeter <= value
            if op == "==": return abs(perimeter - value) < 0.001
        
        return False
    
    def process_command(self, command: str):
        if not command.strip():
            return
        
        parts = command.split(maxsplit=1)
        cmd = parts[0]
        
        if cmd == "ADD":
            data = parts[1] if len(parts) > 1 else ""
            shape = self.parse_add_command(data)
            if shape:
                self.shapes.append(shape)
                print(f"Добавлена фигура: {shape}")
        
        elif cmd == "REM":
            condition = parts[1] if len(parts) > 1 else ""
            initial_count = len(self.shapes)
            self.shapes = [shape for shape in self.shapes 
                          if not self.matches_condition(shape, condition)]
            removed = initial_count - len(self.shapes)
            print(f"Удалено фигур: {removed}")
        
        elif cmd == "PRINT":
            self.print_all()
    
    def print_all(self):
        print("\n=== СОДЕРЖИМОЕ КОНТЕЙНЕРА ===")
        for shape in self.shapes:
            print(shape)
        print(f"Всего фигур: {len(self.shapes)}")
        print("============================")
    
    def clear(self):
        self.shapes.clear()


def create_test_files():
    """Создает примеры тестовых файлов"""
    os.makedirs('tests', exist_ok=True)
    
    # Тест 1: Базовые операции
    test1 = """# Базовый тест: добавление и удаление фигур
                ADD CIRCLE 10 20 5 красный
                ADD RECTANGLE 1.5 2.5 6.5 8.5 синий
                ADD TRIANGLE 0 0 3 0 0 4 зеленый
                PRINT
                REM area > 10
                PRINT"""
    
    with open('tests/test_basic.txt', 'w', encoding='utf-8') as f:
        f.write(test1)
    
    # Тест 2: Сложные условия
    test2 = """# Тест сложных условий
                ADD CIRCLE 10 20 5 красный
                ADD CIRCLE 5 5 2 оранжевый
                ADD CIRCLE 15 15 1 желтый
                ADD RECTANGLE 0 0 2 2 зеленый
                ADD TRIANGLE 0 0 3 0 0 4 голубой
                PRINT
                REM area > 10
                PRINT
                REM area < 5
                PRINT
                REM perimeter > 15
                PRINT"""
    
    with open('tests/test_advanced.txt', 'w', encoding='utf-8') as f:
        f.write(test2)
    
    # Тест 3: Граничные случаи
    test3 = """# Тест граничных случаев
                ADD CIRCLE 0 0 1 красный
                ADD CIRCLE 0 0 2 синий
                ADD RECTANGLE 0 0 1 1 фиолетовый
                PRINT
                REM area > 10
                PRINT
                REM area == 3.14
                PRINT
                REM area >= 12.56
                PRINT"""
    
    with open('tests/test_edge_cases.txt', 'w', encoding='utf-8') as f:
        f.write(test3)
    
    print("Созданы тестовые файлы в папке 'tests'")


if __name__ == "__main__":

    with open("output.txt", "w", encoding="utf-8") as f:
        with redirect_stdout(f):

            create_test_files()

            print("\n" + "="*50)
            print("ДЕМОНСТРАЦИЯ РАБОТЫ С ТЕСТОВЫМИ ФАЙЛАМИ")
            print("="*50)

            parser = CommandParser()
            test_files = ['test_basic.txt', 'test_advanced.txt', 'test_edge_cases.txt']

            for test_file in test_files:
                print(f"\n!!!!!!!!!!!!!!!! Выполнение тестового файла: {test_file}")
                print("-" * 40)

                test_path = os.path.join('tests', test_file)
                try:
                    with open(test_path, 'r', encoding='utf-8') as f2:
                        for line in f2:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                print(f"Выполняется: {line}")
                                parser.process_command(line)
                    print("✅ Файл выполнен успешно")
                except FileNotFoundError:
                    print(f"❌ Файл {test_file} не найден")

                parser.clear()
