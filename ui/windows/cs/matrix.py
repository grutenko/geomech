import numpy as np
import wx

from ui.icon import get_icon


class CreateTransfMatrixWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Утилита нахождения матрицы перехода",
            style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX | wx.FRAME_FLOAT_ON_PARENT,
            size=wx.Size(250, 380),
        )
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()
        self.SetBackgroundColour(wx.NullColour)

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(top_sizer)

        # Создаем панель и элементы интерфейса
        vbox = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(vbox, 1, wx.EXPAND | wx.ALL, border=10)

        self.input_points = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(200, 50))
        self.output_points = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(200, 50))
        self.result_matrix = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(200, 50))
        self.origin_point = wx.TextCtrl(self, style=wx.TE_READONLY, size=(300, 25))

        calculate_btn = wx.Button(self, label="Рассчитать матрицу")
        calculate_btn.Bind(wx.EVT_BUTTON, self.on_calculate)

        vbox.Add(wx.StaticText(self, label="Точки в системе 1 (формат: x1 y1; x2 y2; ...)"))
        vbox.Add(self.input_points, flag=wx.EXPAND | wx.BOTTOM, border=10)
        vbox.Add(wx.StaticText(self, label="Точки в системе 2 (формат: x1 y1; x2 y2; ...)"))
        vbox.Add(self.output_points, flag=wx.EXPAND | wx.BOTTOM, border=10)
        vbox.Add(calculate_btn, flag=wx.BOTTOM, border=10)
        vbox.Add(wx.StaticText(self, label="Матрица"))
        vbox.Add(self.result_matrix, flag=wx.EXPAND | wx.BOTTOM, border=10)
        vbox.Add(wx.StaticText(self, label="Положение начала"))
        vbox.Add(self.origin_point, flag=wx.EXPAND | wx.BOTTOM, border=10)

        self.SetSizer(top_sizer)
        self.Layout()

    def calculate_origin(self, matrix):
        # Преобразование точки (0, 0) в новой системе координат
        origin = np.dot(matrix, [0, 0, 1])
        return origin[:2]

    def format_matrix(self, matrix):
        # Преобразуем каждую строку матрицы в строку с разделением элементов через ';'
        formatted_rows = [";\t".join(map(str, row)) for row in matrix]
        # Соединяем строки с переводом на новую строку
        formatted_matrix = "\n".join(formatted_rows)
        return formatted_matrix

    def on_calculate(self, event):
        # Получаем точки от пользователя
        input_pts_str = self.input_points.GetValue()
        output_pts_str = self.output_points.GetValue()

        # Преобразуем строки в списки точек
        input_pts = self.parse_points(input_pts_str)
        output_pts = self.parse_points(output_pts_str)

        if len(input_pts) < 3 or len(output_pts) < 3:
            wx.MessageBox("At least 3 points are required for the transformation", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Рассчитываем матрицу преобразования
        transformation_matrix = self.calculate_transformation(input_pts, output_pts)
        if transformation_matrix is not None:
            self.result_matrix.SetValue(self.format_matrix(transformation_matrix))
            origin = self.calculate_origin(transformation_matrix)
            self.origin_point.SetValue(f"{origin[0]:.2f}; {origin[1]:.2f}")

    def parse_points(self, points_str):
        points = []
        try:
            points = [list(map(float, point.split())) for point in points_str.split(";")]
        except ValueError:
            wx.MessageBox("Invalid input format. Please enter points in 'x y; x y' format.", "Error", wx.OK | wx.ICON_ERROR)
        return points

    def calculate_transformation(self, input_pts, output_pts):
        # Решаем систему линейных уравнений для нахождения матрицы 3x3
        A = []
        B = []

        for (x_in, y_in), (x_out, y_out) in zip(input_pts, output_pts):
            A.append([x_in, y_in, 1, 0, 0, 0, -x_in * x_out, -y_in * x_out])
            A.append([0, 0, 0, x_in, y_in, 1, -x_in * y_out, -y_in * y_out])
            B.append(x_out)
            B.append(y_out)

        A = np.array(A)
        B = np.array(B)

        try:
            # Решаем уравнение A * M = B для M
            transformation_vector, _, _, _ = np.linalg.lstsq(A, B, rcond=None)

            # Вектор преобразования имеет вид [a, b, tx, c, d, ty, p1, p2]
            transformation_matrix = np.array(
                [
                    [transformation_vector[0], transformation_vector[1], transformation_vector[2]],
                    [transformation_vector[3], transformation_vector[4], transformation_vector[5]],
                    [transformation_vector[6], transformation_vector[7], 1],
                ]
            )
        except np.linalg.LinAlgError:
            wx.MessageBox("Error calculating transformation", "Error", wx.OK | wx.ICON_ERROR)
            return None

        return transformation_matrix
