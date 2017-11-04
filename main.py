from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from mLexer import mLexer
from mParser import mParser
from mVisitor import mVisitor
from antlr4 import CommonTokenStream
from antlr4.FileStream import InputStream
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
import math


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
            # Leaving variable's row
            Color(*self.highlight)
            self.leaving_variable_row_background = Rectangle(
                pos=(200, self.height * (self.number_of_iterations - self.iteration - 1) + 30 * (
                    self.constraints - self.leaving_variable)),
                size=(self.variables * 200, 30))
            # Entering variable's column
            Color(*self.highlight)
            self.entering_variable_row_background = Rectangle(pos=(
                200 + self.entering_variable * 200, 30 + self.height * (self.number_of_iterations - self.iteration - 1)),
                size=(200, self.constraints * 30))
            # Pivot
            Color(*self.pivot)
            self.pivot_background = Rectangle(
                pos=(200 + 200 * self.entering_variable,
                     self.height * (self.number_of_iterations - self.iteration - 1) + 30 * (self.constraints - self.leaving_variable)),
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
                             size_hint=(None, None), size=(100, 30))  # , size_hint=(None, None), height=30)
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


class Gui(GridLayout):
    def __init__(self, **kwargs):
        # create a default grid layout with custom width/height
        super(Gui, self).__init__(**kwargs)

        with self.canvas:
            Color(0, 0, 0, 0)
            Rectangle(pos=self.pos, size=self.size)

        # when we add children to the grid layout, its size doesn't change at
        # all. we need to ensure that the height will be the minimum required
        # to contain all the childs. (otherwise, we'll child outside the
        # bounding box of the childs)
        self.bind(minimum_height=self.setter('height'))
        self.bind(minimum_width=self.setter('width'))

        # How many variables has the problem?
        self.add_widget(
            Label(text="How many decision variables has the problem?", size_hint=(None, None), size=(400, 30)))
        self.number_of_variables = TextInput(size_hint=(None, None), size=(300, 30))
        self.add_widget(self.number_of_variables)

        # How many constraints?
        self.add_widget(
            Label(text="How many restrictions?"))
        self.number_of_constraints = TextInput(size_hint=(None, None), size=(300, 30))
        self.add_widget(self.number_of_constraints)

        self.submit = Button(text="Continue", size_hint=(None, None), size=(400, 30))
        self.submit.bind(on_press=self.gen_input_table)
        self.add_widget(self.submit)

        self.fo = None
        self.type = None
        self.open_type = None
        self.constraints = []
        self.constraints_types = []

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
        self.open_type = Button(text="Maximize", size_hint=(None, None), size=(100, 44))
        self.open_type.bind(on_release=self.type.open)
        self.type.bind(on_select=lambda instance, x: setattr(self.open_type, "text", x))

        self.add_widget(self.open_type)

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

        self.submit = Button(size_hint=(None, None), size=(400, 30))
        self.submit.bind(on_press=self.big_m)
        self.submit.text = "Continue"
        self.add_widget(self.submit)

    def big_m(self, e):
        variables = int(self.number_of_variables.text)
        constraints = int(self.number_of_constraints.text)
        self.clear_widgets()
        problem_type = self.open_type.text
        # Coefficients of the objective function
        cj = [str(x.get()) for x in
              filter(lambda y: type(y) == Variable, self.fo.children)]
        cj.reverse()
        a = [x.get_coefficients() for x in self.constraints]  # Coefficients of the constraints' variables
        b = [x.get_rhs() for x in self.constraints]  # Rhs
        constraint_types = [x.get_type() for x in self.constraints]
        variable_names = ["x" + str(i) for i in range(1, variables + 1)]
        iteration = 0
        # Let's create the initial optimal solution
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
        output_table = []
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

            # Find the entering variable
            entering_variable = cj_minus_zj[0]  # min or max cj-zj (depending on the problem)
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

            # get the pivot
            pivot = a[leaving_variable_index][entering_variable_index]

            # do the pivoting operations
            # First we divide the row of the pivot by the pivot
            output_table.append(
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
                    if "a" in basic_vars[i] and self.parse_m(cb[i] + "> 0.0"):
                        special = True
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
            iteration += 1
        self.add_widget(Label(text="Final solution:", size_hint=(None, None), size=(100, 30)))
        self.add_widget(
            Label(text=(("Zmax = " if problem_type == "Maximize" else "Zmin = ") + zj[-1]), size_hint=(None, None),
                  size=(250, 30)))
        basic_vars = [(x[:-1] + "x" if x[-1] == "h" else x) for x in basic_vars]
        for x in variable_names[:variables]:
            if x in basic_vars:
                self.add_widget(
                    Label(text=(x + " = " + str(b[basic_vars.index(x)])), size_hint=(None, None), size=(250, 30)))
            else:
                self.add_widget(Label(text=(x + " = 0.0"), size_hint=(None, None), size=(250, 30)))
        for i in range(len(output_table)):
            output_table[i].number_of_iterations = len(output_table)
            self.add_widget(output_table[i])

    @classmethod
    def parse_m(cls, m_expression):
        _input = InputStream(m_expression)
        lexer = mLexer(_input)
        stream = CommonTokenStream(lexer)
        parser = mParser(stream)
        tree = parser.start_rule()
        visitor = mVisitor()
        return visitor.visit(tree)


class Simplex(App):
    def build(self):
        gui = Gui(cols=2,
                  size_hint=(None, None), width=Window.width)
        scroll_view = ScrollView(size_hint=(None, None), size=(Window.width, Window.height), do_scroll_x=True)
        scroll_view.add_widget(gui)
        return scroll_view


if __name__ == '__main__':
    Simplex().run()