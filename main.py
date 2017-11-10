import math
import os

from antlr4 import CommonTokenStream
from antlr4.FileStream import InputStream
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

from mLexer import mLexer
from mParser import mParser
from mVisitor import mVisitor


class OutputTable(GridLayout):
    def __init__(self, iteration, cj, variable_names, zj, cb, basic_vars, b, cj_minus_zj, entering_variable,
                 leaving_variable, a, number_of_iterations, **kwargs):
        super(OutputTable, self).__init__(**kwargs)
        self.cols = len(variable_names) + 3

        self.background_width = None
        self.background_height = None

        self.bind(minimum_height=self.setter('height'))
        self.bind(minimum_height=lambda x, y: self.resize_background("height", x, y))
        self.bind(minimum_width=self.setter('width'))
        self.bind(minimum_width=lambda x, y: self.resize_background("width", x, y))

        # Colors for the output table
        self.base1 = list(map(lambda x: (x / 255), [0, 43, 54, 255]))
        self.base2 = list(map(lambda x: (x / 255), [7, 54, 66, 255]))
        self.error = list(map(lambda x: (x / 255), [220, 50, 47, 255]))
        self.pivot = list(map(lambda x: (x / 255), [133, 153, 0, 255]))
        self.highlight = list(map(lambda x: (x / 255), [38, 139, 210, 255]))

        self.background = None
        self.pivot_background = None
        self.leaving_variable_row_background = None
        self.entering_variable_row_background = None
        self.entering_variable = entering_variable
        self.leaving_variable = leaving_variable
        self.variables = len(variable_names)
        self.constraints = len(cb)
        self.number_of_iterations = number_of_iterations
        self.iteration = iteration

        # First row: Iteration number and a padding of empty labels
        self.add_widget(Label(text=("Iter: " + str(iteration)), size_hint=(None, None), size=(100, 30)))
        for i in range(len(variable_names) + 2):
            self.add_widget(Label(size_hint=(None, None), size=(100, 30)))

        # Second row: 'Cj', and empty label, the actual values of Cj and another empty label
        self.add_widget(Label(text="Cj", size_hint=(None, None), size=(100, 30)))
        self.add_widget(Label(size_hint=(None, None), size=(100, 30)))
        for x in cj:
            self.add_widget(Label(text=x, size_hint=(None, None), size=(200, 30)))
        self.add_widget(Label(size_hint=(None, None), size=(100, 30)))

        # Third row: 'Cb', 'VarB' followed by the names of the variables and then 'bi'
        self.add_widget(Label(text="Cb", size_hint=(None, None), size=(100, 30)))
        self.add_widget(Label(text="VarB", size_hint=(None, None), size=(100, 30)))
        for x in variable_names:
            self.add_widget(Label(text=x, size_hint=(None, None), size=(200, 30)))
        self.add_widget(Label(text="bi", size_hint=(None, None), size=(200, 30)))

        # Fourth row: empty label, 'Zj', the actual values of Zj
        self.add_widget(Label(size_hint=(None, None), size=(100, 30)))
        self.add_widget(Label(text="Zj", size_hint=(None, None), size=(100, 30)))
        for x in zj:
            self.add_widget(Label(text=x, size_hint=(None, None), size=(200, 30)))

        # Fifth to N-1th row: Cb[i], basic_variables[i], a[i][0]...a[i][len(a[i]) - 1], b[i]
        for i in range(len(a)):
            self.add_widget(Label(text=str(cb[i]), size_hint=(None, None), size=(100, 30)))
            self.add_widget(Label(text=str(basic_vars[i]), size_hint=(None, None), size=(100, 30)))
            for j in range(len(a[i])):
                new_label = Label(text=str(a[i][j]), size_hint=(None, None), size=(200, 30))
                self.add_widget(new_label)
            self.add_widget(
                Label(text=str(b[i]), size_hint=(None, None), size=(200, 30)))
        # Nth row: 'Cj - Zj', the actual value of cj_minus_zj and then an empty label
        self.add_widget(Label(text="Cj - Zj", size_hint=(None, None), size=(100, 30)))
        self.add_widget(Label(size_hint=(None, None), size=(100, 30)))
        for x in cj_minus_zj:
            self.add_widget(Label(text=x, size_hint=(None, None), size=(200, 30)))
        self.add_widget(Label(size_hint=(None, None), size=(100, 30)))

    def resize_background(self, s, x, y):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.base1)
            self.background = Rectangle(
                pos=(self.x, self.height * (self.number_of_iterations - self.iteration - 1)),
                size=self.size)
            if self.entering_variable is not None:
                # Leaving variable's row
                Color(*self.highlight)
                self.leaving_variable_row_background = Rectangle(
                    pos=(200, self.height * (self.number_of_iterations - self.iteration - 1) + 30 * (
                        self.constraints - self.leaving_variable)),
                    size=(self.variables * 200, 30))
                # Entering variable's column
                Color(*self.highlight)
                self.entering_variable_row_background = Rectangle(pos=(
                    200 + self.entering_variable * 200,
                    30 + self.height * (self.number_of_iterations - self.iteration - 1)),
                    size=(200, self.constraints * 30))
                # Pivot
                Color(*self.pivot)
                self.pivot_background = Rectangle(
                    pos=(200 + 200 * self.entering_variable,
                         self.height * (self.number_of_iterations - self.iteration - 1) + 30 * (
                             self.constraints - self.leaving_variable)),
                    size=(200, 30))
            else:
                Color(*self.pivot)
                self.pivot_background = Rectangle(pos=(200 + 200 * self.variables, 30 + 30 * self.constraints),
                                                  size=(200, 30))


class Constraint(GridLayout):
    def __init__(self, variables, **kwargs):
        super(Constraint, self).__init__(**kwargs)
        self.variables = []

        self.bind(minimum_height=self.setter('height'))
        self.bind(minimum_width=self.setter('width'))

        for x in range(1, variables + 1):
            self.variables.append(Variable(x, x == variables, cols=2,
                                           size_hint=(None, None), size=(200, 30)))

        for i in range(len(self.variables)):
            self.add_widget(self.variables[i])
        self.type = DropDown()
        for x in ["<=", ">=", "="]:
            btn = Button(text=x, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.type.select(btn.text))
            self.type.add_widget(btn)
        self.open_type = Button(text="<=", size_hint=(None, None), size=(50, 30))
        self.open_type.bind(on_release=self.type.open)
        self.type.bind(on_select=lambda instance, x: setattr(self.open_type, "text", x))

        self.add_widget(self.open_type)

        self.rhs = TextInput(multiline=False,
                             size_hint=(None, None), size=(100, 30))
        self.add_widget(self.rhs)

    def get_coefficients(self):
        coefficients = []
        for x in self.variables:
            coefficients.append(x.get())
        return coefficients

    def get_rhs(self):
        try:
            return float(self.rhs.text)
        except ValueError:
            return 0.0

    def get_type(self):
        return self.open_type.text


class Variable(GridLayout):
    def __init__(self, i, last, **kwargs):
        super(Variable, self).__init__(**kwargs)

        self.bind(minimum_height=self.setter('height'))
        self.bind(minimum_width=self.setter('width'))
        self.var = TextInput(multiline=False)
        self.add_widget(self.var)
        self.add_widget(Label(text=("X" + str(i) + ("" if last else " +"))))

    def get(self):
        try:
            return float(self.var.text)
        except ValueError:
            return 0.0


class SaveDialog(GridLayout):
    def __init__(self, save=None, dismiss=None):
        super(SaveDialog, self).__init__()
        self.cols = 1

        self.save = save
        self.dismiss = dismiss
        self.text_input = TextInput(size_hint_y=None, height=30, multiline=False)
        self.file_chooser = FileChooserListView()
        self.save_btn = Button(text="Save", size_hint_y=None, height=30)
        self.save_btn.bind(on_release=lambda e: self.save(self.file_chooser.path, self.text_input.text))
        self.cancel_btn = Button(text="Cancel", size_hint_y=None, height=30)
        self.cancel_btn.bind(on_release=self.dismiss)

        self.add_widget(self.file_chooser)
        self.add_widget(self.text_input)
        self.add_widget(self.save_btn)
        self.add_widget(self.cancel_btn)


class Gui(GridLayout):
    def __init__(self, **kwargs):
        # create a default grid layout with custom width/height
        super(Gui, self).__init__(**kwargs)

        with self.canvas:
            Color(0, 0, 0, 0)
            Rectangle(pos=self.pos, size=self.size)

        self.base1 = list(map(lambda x: (x / 255), [0, 43, 54, 255]))
        self.base2 = list(map(lambda x: (x / 255), [7, 54, 66, 255]))
        self.base3 = list(map(lambda x: (x / 255), [253, 246, 227, 255]))
        self.error = list(map(lambda x: (x / 255), [220, 50, 47, 255]))
        self.pivot = list(map(lambda x: (x / 255), [133, 153, 0, 255]))
        self.highlight = list(map(lambda x: (x / 255), [38, 139, 210, 255]))

        # when we add children to the grid layout, its size doesn't change at
        # all. we need to ensure that the height will be the minimum required
        # to contain all the childs. (otherwise, we'll child outside the
        # bounding box of the childs)
        self.bind(minimum_height=self.setter('height'))
        self.bind(minimum_width=self.setter('width'))

        # How many variables has the problem?
        self.add_widget(
            Label(text="How many decision variables has the problem?", size_hint=(None, None), size=(400, 30)))
        self.number_of_variables = TextInput(size_hint=(None, None), size=(400, 30))
        self.add_widget(self.number_of_variables)

        # How many constraints?
        self.add_widget(
            Label(text="How many restrictions?"))
        self.number_of_constraints = TextInput(size_hint=(None, None), size=(400, 30))
        self.add_widget(self.number_of_constraints)

        # Type of the problem
        self.problem_nature = DropDown()
        for x in ["Linear Programming", "Integer Linear Programming"]:
            btn = Button(text=x, size_hint_y=None, height=30)
            btn.bind(on_release=lambda btn: self.problem_nature.select(btn.text))
            self.problem_nature.add_widget(btn)
        self.open_problem_nature = Button(text="Linear Programming", size_hint=(None, None), size=(400, 30))
        self.open_problem_nature.bind(on_release=self.problem_nature.open)
        self.problem_nature.bind(on_select=lambda instance, x: setattr(self.open_problem_nature, "text", x))

        self.add_widget(Label(text="Type of the problem:", size_hint=(None, None), size=(400, 30)))
        self.add_widget(self.open_problem_nature)

        self.submit = Button(text="Continue", size_hint=(None, None), size=(400, 30))
        self.submit.bind(on_release=self.gen_input_table)
        self.add_widget(self.submit)

        self.fo = None
        self.type = None
        self.open_problem_type = None
        self.integer_check = []
        self.constraints = []
        self.constraints_types = []
        self._popup = None

    def gen_input_table(self, e):
        variables = int(self.number_of_variables.text)
        constraints = int(self.number_of_constraints.text)
        self.clear_widgets()
        self.cols = 1

        self.type = DropDown()
        for x in ["Maximize", "Minimize"]:
            btn = Button(text=x, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.type.select(btn.text))
            self.type.add_widget(btn)
        self.open_problem_type = Button(text="Maximize", size_hint=(None, None), size=(100, 44))
        self.open_problem_type.bind(on_release=self.type.open)
        self.type.bind(on_select=lambda instance, x: setattr(self.open_problem_type, "text", x))

        self.add_widget(self.open_problem_type)

        self.fo = GridLayout(cols=(variables + 1), padding=10, spacing=10,
                             size_hint=(None, None), width=Window.width)

        self.fo.bind(minimum_height=self.setter('height'))
        self.fo.bind(minimum_width=self.setter('width'))

        self.fo.add_widget(Label(text="Objective funtion: ", size_hint=(None, None), size=(150, 30)))
        for i in range(1, variables + 1):
            self.fo.add_widget(Variable(i, i == variables, cols=2,
                                        size_hint=(None, None), size=(200, 30)))

        self.add_widget(self.fo)

        self.add_widget(Label(text="Subject to:", size_hint=(None, None), size=(200, 50)))

        self.constraints = []

        for i in range(1, constraints + 1):
            self.constraints.append(Constraint(variables, cols=(variables + 2), padding=10, spacing=10,
                                               size_hint=(None, None), width=Window.width))
            self.add_widget(self.constraints[i - 1])

        self.integer_check = []
        if self.open_problem_nature.text == "Integer Linear Programming":
            self.add_widget(
                Label(text="The following variables must be integers:", size_hint=(None, None), size=(400, 30)))
            for i in range(variables):
                new_container = GridLayout(cols=2, size_hint=(None, None), width=125)
                new_container.add_widget(Label(text=("x" + str(i)), size=(100, 30)))
                new_check_box = CheckBox()
                self.integer_check.append(new_check_box)
                new_container.add_widget(new_check_box)
                self.add_widget(new_container)

        self.submit = Button(size_hint=(None, None), size=(400, 30))
        self.submit.bind(on_release=self.solve)
        self.submit.text = "Continue"
        self.add_widget(self.submit)

    def solve(self, e):
        variables = int(self.number_of_variables.text)
        constraints = int(self.number_of_constraints.text)
        self.clear_widgets()
        problem_type = self.open_problem_type.text
        problem_nature = self.open_problem_nature.text
        # Coefficients of the objective function
        cj = [str(x.get()) for x in
              filter(lambda y: type(y) == Variable, self.fo.children)]
        cj.reverse()
        a = [x.get_coefficients() for x in self.constraints]  # Coefficients of the constraints' variables
        b = [x.get_rhs() for x in self.constraints]  # Rhs
        constraint_types = [x.get_type() for x in self.constraints]
        variable_names = ["x" + str(i) for i in range(1, variables + 1)]
        iteration = 0
        if problem_nature == "Linear Programming":
            s = Simplex(variables, constraints, cj, a, b, constraint_types, variable_names, problem_type)
            output_tables, solution, basic_vars = s.solve()
            self.add_widget(Label(text="Final solution:", size_hint=(None, None), size=(100, 30)))
            self.add_widget(
                Label(text=(("Zmax = " if problem_type == "Maximize" else "Zmin = ") + str(solution[0])),
                      size_hint=(None, None),
                      size=(250, 30)))
            basic_vars = [(x[:-1] + "x" if x[-1] == "h" else x) for x in basic_vars]
            for i in range(1, len(solution)):
                self.add_widget(Label(text=("x" + str(i) + " = " + str(solution[i])), size_hint=(None, None),
                                      size=(250, 30)))
            for i in range(len(output_tables)):
                self.add_widget(output_tables[i])
        else:  # Integer linear programming
            integer_check = [x.active for x in self.integer_check]
            height = 0
            # Initial problem
            problems = [[Simplex(variables, constraints, cj[:], [x[:] for x in a], b[:], constraint_types[:],
                                 variable_names, problem_type)]]
            optimal_solution_aux = -math.inf if problem_type == "Maximize" else math.inf
            optimal_solution = None
            while True:
                for x in problems[height]:
                    if x is not None:
                        x.solve()

                problems.append([])
                for i in range(len(problems[height])):
                    if problems[height][i] is None:
                        problems[height + 1].append(None)
                        problems[height + 1].append(None)
                    else:
                        solution = problems[height][i].solution
                        if solution is None:
                            problems[height + 1].append(None)
                            problems[height + 1].append(None)
                        else:
                            new_iter = False
                            for k in range(1, len(solution)):
                                if integer_check[k - 1] and not solution[k].is_integer():
                                    new_iter = True
                                    np1 = Simplex.from_simplex(problems[height][i]).add_constraint(
                                        [0.0 for l in range(k - 1)] + [1.0] + [0.0 for l in
                                                                               range(len(solution) - k - 1)],
                                        "<=",
                                        int(solution[k]))
                                    np2 = Simplex.from_simplex(problems[height][i]).add_constraint(
                                        [0.0 for l in range(k - 1)] + [1.0] + [0.0 for l in
                                                                               range(len(solution) - k - 1)],
                                        ">=",
                                        int(solution[k]) + 1)
                                    problems[height + 1].append(np1)
                                    problems[height + 1].append(np2)
                                    break
                            if not new_iter:
                                if problem_type == "Maximize":
                                    if optimal_solution_aux < solution[0]:
                                        optimal_solution_aux = solution[0]
                                        optimal_solution = solution
                                else:
                                    if optimal_solution_aux > solution[0]:
                                        optimal_solution_aux = solution[0]
                                        optimal_solution = solution
                                problems[height + 1].append(None)
                                problems[height + 1].append(None)
                if not any(problems[height + 1]):
                    break
                height += 1

            # It's time to print the tree to the gui
            text_height = 30 * variables + 30
            text_width = 200
            sibling_spacing = text_width
            layout = FloatLayout(size_hint=(None, None), size=(
                text_width * len(problems[-1]) + text_width, text_height * len(problems) + 100 * len(problems)))
            for i in range(len(problems) - 1):
                for j in range(len(problems[i])):
                    if problems[i][j] is not None:
                        base_width = ((sibling_spacing * j * (len(problems[-1])) /
                                       len(problems[i])) + sibling_spacing * (
                                          len(problems[-1]) / (2 ** (i + 1))))
                        base_height = text_height * (len(problems) - i) + 100 * (len(problems) - i - 1)

                        if i != len(problems) - 2 and (
                                        problems[i + 1][j * 2] is None or problems[i][j].solution is None) and i != 0:
                            base_width = ((sibling_spacing * (j // 2) * (len(problems[-1])) /
                                           len(problems[i - 1])) + sibling_spacing * (
                                              len(problems[-1]) / (2 ** i))) + (
                                             text_width * 2 if (j + 1) % 2 == 0 else - text_width * 2)

                        if problems[i][j].solution is None:
                            text = "infeasible"
                            color = self.error
                        else:
                            color = self.base2
                            if problems[i][j].solution[0] == optimal_solution[0]:
                                color = self.highlight
                            text = ("Zmax = " if problem_type == "Maximize" else "Zmin = ") + str(
                                problems[i][j].solution[
                                    0]) + "\n"
                            for k in range(1, len(problems[i][j].solution)):
                                text += "x" + str(k) + " = " + str(problems[i][j].solution[k]) + "\n"

                        if i != 0:
                            layout.add_widget(
                                Label(text=(
                                    "x" + str(problems[i][j].a[-1].index(1.0) + 1) + " " +
                                    problems[i][j].constraint_types[
                                        -1] + " " + str(problems[i][j].b[-1])),
                                    pos=(
                                        base_width,
                                        base_height + text_height / 2 + 15),
                                    size=(text_width, text_height), size_hint=(None, None)))

                            with self.canvas.before:
                                Color(*self.pivot)
                                Line(points=(
                                    base_width + text_width / 2,
                                    base_height + text_height,
                                    text_width / 2 +
                                    ((sibling_spacing * (j // 2) * (len(problems[-1])) /
                                      len(problems[i - 1])) + sibling_spacing * (
                                         len(problems[-1]) / (2 ** i))), text_height +
                                    base_height + 100), width=1)

                        with self.canvas.before:
                            Color(*color)
                            Rectangle(pos=(base_width,
                                           base_height),
                                      size=(text_width, text_height))

                            Color(*self.base3)
                            Line(points=(
                                base_width, base_height, base_width, base_height + text_height,
                                base_width + text_width,
                                base_height + text_height, base_width + text_width, base_height, base_width,
                                base_height, base_width + text_width, base_height), width=1)

                        layout.add_widget(Label(text=text,
                                                pos=(
                                                    base_width,
                                                    base_height),
                                                size=(text_width, text_height), size_hint=(None, None)))
            # Printing the optimal solution
            text = "Optimal solution\n" + ("Zmax = " if problem_type == "Maximize" else "Zmin = ") + str(
                optimal_solution[0]) + "\n"
            for i in range(1, len(optimal_solution)):
                text += "x" + str(i) + " = " + str(optimal_solution[i]) + "\n"
            new_label = Label(text=text, size=(text_width, text_height),
                              pos=(0, len(problems) * text_height + 100 * (len(problems) - 1)), size_hint=(None, None))
            with self.canvas.before:
                Color(*self.highlight)
                Rectangle(pos=new_label.pos, size=new_label.size)
            layout.add_widget(new_label)

            layout.add_widget(
                Label(text="The spanning tree is on the right side of the window ->",
                      pos=(new_label.x + 200, new_label.y),
                      size_hint=(None, None), size=(400, 30)))

            save_btn = Button(text="Export as png", size=(text_width, 30),
                              pos=(0, len(problems) * text_height - 30 + 100 * (len(problems) - 1)),
                              size_hint=(None, None))
            save_btn.bind(on_release=self.show_save)
            layout.add_widget(save_btn)
            self.add_widget(layout)

    def show_save(self, btn):
        content = SaveDialog(save=self.save, dismiss=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def dismiss_popup(self, e):
        self._popup.dismiss()

    def save(self, path, filename):
        if self.open_problem_nature.text == "Integer Linear Programming":
            f = os.path.join(path, filename)
            self.export_to_png(f + ".png" if ".png" not in f else f)
        self._popup.dismiss()


class Simplex:
    def __init__(self, number_of_variables=None, number_of_constraints=None, cj=None, a=None, b=None,
                 constraint_types=None, variable_names=None, problem_type=None):
        self.solved = False
        self.number_of_variables = number_of_variables
        self.number_of_constraints = number_of_constraints
        self.cj = cj
        self.a = a
        self.b = b
        self.constraint_types = constraint_types
        self.variable_names = variable_names
        self.problem_type = problem_type
        self.solution = None
        self.output_tables = None

    def solve(self):
        variables = self.number_of_variables
        constraints = self.number_of_constraints
        cj = self.cj[:]
        a = [x[:] for x in self.a]
        b = self.b[:]
        constraint_types = self.constraint_types[:]
        variable_names = self.variable_names[:]
        problem_type = self.problem_type
        # Let's create the initial optimal solution
        iteration = 0
        for i in range(constraints):
            if constraint_types[i] == ">=":
                _type = 0
            elif constraint_types[i] == "<=":
                _type = 2
            else:  # =
                _type = 1
            constraint_types[i] = [constraint_types[i], _type]
            b[i] = [b[i], _type]

        for i in range(constraints):
            a[i].append(constraint_types[i][1])

        constraint_types.sort(key=lambda c: c[1])
        a.sort(key=lambda ai: ai[-1])
        b.sort(key=lambda bj: bj[-1])

        for i in range(constraints):
            a[i] = a[i][:-1]
            constraint_types[i] = constraint_types[i][0]
            b[i] = b[i][0]

        # Now I want to see the identity matrix
        gt_constraints = constraint_types.count(">=")
        variable_names += ["e" + str(i) for i in range(1, gt_constraints + 1)]
        variable_names += ["a" + str(i) for i in range(1, gt_constraints + 1)]
        eq_constraints = constraint_types.count("=")
        variable_names += ["a" + str(i) for i in range(gt_constraints + 1, eq_constraints + gt_constraints + 1)]
        lt_constraints = constraint_types.count("<=")
        variable_names += ["h" + str(i) for i in range(1, lt_constraints + 1)]

        cj_minus_zj = ["0.0" for x in range(variables + gt_constraints * 2 + eq_constraints + lt_constraints)]
        zj = cj_minus_zj[:]

        basic_vars = variable_names[variables + gt_constraints:]

        cj += ["0.0" for x in range(gt_constraints)]
        if problem_type == "Maximize":
            cj += ["-m" for x in range(gt_constraints + eq_constraints)]
        else:  # Minimize
            cj += ["m" for x in range(gt_constraints + eq_constraints)]
        cj += ["0.0" for x in range(lt_constraints)]

        cb = [cj[i] for i in
              range(variables + gt_constraints, variables + gt_constraints * 2 + eq_constraints + lt_constraints)]
        for i in range(len(a)):
            a[i] += [0.0 for i in range(gt_constraints * 2 + eq_constraints + lt_constraints)]

        for i in range(gt_constraints):
            for j in range(variables, variables + gt_constraints):
                if (i + variables) == j:
                    a[i][j] = -1.0

        for i in range(gt_constraints * 2 + eq_constraints + lt_constraints):
            for j in range(variables + gt_constraints,
                           variables + gt_constraints * 2 + eq_constraints + lt_constraints):
                if (i + variables + gt_constraints) == j:
                    a[i][j] = 1.0

        # Now it's time to iterate until the job is done
        end = False
        special = False
        self.output_tables = []
        self.solution = []
        while not end:
            # reset z to zeroes
            zj = ["0.0" for x in range(variables + gt_constraints * 2 + eq_constraints + lt_constraints + 1)]
            # Calculate zj
            for i in range(len(a[0])):
                for j in range(len(a)):
                    new_zj = self.parse_m(zj[i] + "+" + str(a[j][i]) + str("*") + cb[j])
                    zj[i] = new_zj["rhs"] + "+" + new_zj["m_coefficient"] + "m"

            # updating the value of the solution
            for i in range(len(b)):
                aux = self.parse_m(zj[-1] + "+" + cb[i] + "*" + str(b[i]))
                zj[-1] = aux["rhs"] + "+" + aux["m_coefficient"] + "m"

            # calculate cj - zj
            for i in range(len(cj_minus_zj)):
                new_cj_minus_zj = self.parse_m(cj[i] + "-(" + zj[i] + ")")
                cj_minus_zj[i] = new_cj_minus_zj["rhs"] + ("+" if "-" not in new_cj_minus_zj["m_coefficient"] else "") + \
                                 new_cj_minus_zj["m_coefficient"] + "m"

            # check if we got to the end or we must stop (the problem is a special case)
            # Checking if we reached the stopping condition
            end = True
            if problem_type == "Maximize":
                for x in cj_minus_zj:
                    if self.parse_m(x + "> 0.0"):
                        end = False
                        break
            else:
                for x in cj_minus_zj:
                    if self.parse_m(x + "< 0.0"):
                        end = False
                        break
            # Checking if this problem is a special case
            if end:
                # 1. No feasible region
                for i in range(len(basic_vars)):
                    if "a" in basic_vars[i] and b[i] > 0.0:
                        special = True
                        self.solution = None
                        break
                # 3. Alternative solutions
                non_basic_vars = []  # Not the actual names, just the index in variable_names
                for i in range(len(variable_names)):
                    if variable_names[i] not in basic_vars:
                        non_basic_vars.append(i)

                for x in non_basic_vars:
                    if zj[x] == "0.0":
                        special = True
                        break

                self.output_tables.append(
                    OutputTable(iteration, cj, variable_names, zj, cb, basic_vars, b, cj_minus_zj,
                                None, None, a, 0, size_hint=(None, None), width=Window.width))
                break

            # Find the entering variable
            entering_variable = cj_minus_zj[0]
            entering_variable_index = 0  # index of the entering variable
            operator = "<" if problem_type == "Maximize" else ">"
            for i in range(len(cj_minus_zj)):
                if self.parse_m(entering_variable + operator + cj_minus_zj[i]):
                    entering_variable = cj_minus_zj[i]
                    entering_variable_index = i

            # Find the leaving variable
            min_ratio = math.inf
            leaving_variable_index = None
            for i in range(len(b)):
                if a[i][entering_variable_index] > 0:
                    if min_ratio > b[i] / a[i][entering_variable_index]:
                        min_ratio = b[i] / a[i][entering_variable_index]
                        leaving_variable_index = i
            # 2. Unbounded solution
            if leaving_variable_index is None:
                special = True

            # Get the pivot
            pivot = a[leaving_variable_index][entering_variable_index]

            # Get the new output table
            self.output_tables.append(
                OutputTable(iteration, cj, variable_names, zj, cb, basic_vars, b, cj_minus_zj, entering_variable_index,
                            leaving_variable_index, a, 0, size_hint=(None, None), width=Window.width))

            # Then we pivot
            for i in range(len(a)):
                # update the bi's
                if i != leaving_variable_index:
                    b[i] -= (a[i][entering_variable_index] * b[leaving_variable_index]) / pivot

            b[leaving_variable_index] /= pivot
            # the row and column of the pivot are left untouched
            for i in range(len(a)):
                for j in range(len(a[0])):
                    if i != leaving_variable_index and j != entering_variable_index:
                        a[i][j] -= (a[i][entering_variable_index] * a[leaving_variable_index][j]) / pivot

            # Update the column of the pivot
            for i in range(len(a)):
                if i != leaving_variable_index:
                    a[i][entering_variable_index] = 0

            # Dividing the pivot's row by the pivot
            a[leaving_variable_index] = [x / pivot for x in a[leaving_variable_index]]

            # Update basic variables list and cb
            basic_vars[leaving_variable_index] = variable_names[entering_variable_index]
            cb[leaving_variable_index] = cj[entering_variable_index]

            iteration += 1
        if self.solution is not None:
            self.solution.append(float(zj[-1][:zj[-1].find("+")]))
            for x in variable_names[:variables]:
                if x in basic_vars:
                    self.solution.append(b[basic_vars.index(x)])
                else:
                    self.solution.append(0.0)
            for i in range(len(self.output_tables)):
                self.output_tables[i].number_of_iterations = len(self.output_tables)
            return self.output_tables, self.solution, basic_vars

    def add_constraint(self, coefficients, constraint_type, rhs):
        self.solved = False
        self.b.append(rhs)
        self.a.append(coefficients)
        self.constraint_types.append(constraint_type)
        self.number_of_constraints += 1
        return self

    @classmethod
    def parse_m(cls, m_expression):
        _input = InputStream(m_expression)
        lexer = mLexer(_input)
        stream = CommonTokenStream(lexer)
        parser = mParser(stream)
        tree = parser.start_rule()
        visitor = mVisitor()
        return visitor.visit(tree)

    @staticmethod
    def from_simplex(s):
        new_simplex = Simplex()
        new_simplex.solved = s.solved
        new_simplex.number_of_variables = s.number_of_variables
        new_simplex.number_of_constraints = s.number_of_constraints
        new_simplex.cj = s.cj[:]
        new_simplex.a = [x[:] for x in s.a]
        new_simplex.b = s.b[:]
        new_simplex.constraint_types = s.constraint_types[:]
        new_simplex.variable_names = s.variable_names[:]
        new_simplex.problem_type = s.problem_type
        return new_simplex


class SimplexApp(App):
    def build(self):
        gui = Gui(cols=2,
                  size_hint=(None, None), width=Window.width)
        scroll_view = ScrollView(size_hint=(None, None), size=(Window.width, Window.height), do_scroll_x=True)
        Window.bind(width=scroll_view.setter('width'))
        Window.bind(height=scroll_view.setter('height'))
        scroll_view.add_widget(gui)
        return scroll_view


if __name__ == '__main__':
    SimplexApp().run()
