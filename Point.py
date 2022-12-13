class Point:
    def __init__(self, x, y, parent, e_point, degree):
        self.x = x
        self.y = y
        self.parent = parent

        if parent is not None:
            if (degree % 90) == 0:
                self.cost = parent.cost + 1
            else:
                self.cost = parent.cost + 1.4
            # self.cost = parent.cost + 1
            # if degree != parent.degree:
            #     self.cost += 1
        else:
            self.cost = 0

        if e_point is None:
            self.h = 0
        else:
            self.h = abs(x - e_point.x) + abs(y - e_point.y)

        self.degree = degree

    def __init__(self, p, parent, e_point, degree):
        self.x = p[0]
        self.y = p[1]
        self.parent = parent



        if parent is not None:
            if (degree % 90) == 0:
                self.cost = parent.cost + 1
            else:
                self.cost = parent.cost + 1.4
        else:
            self.cost = 0

        if e_point is None:
            self.h = 0
        else:
            self.h = abs(p[0] - e_point.x) + abs(p[1] - e_point.y)

        self.degree = degree

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def get_cost_func(self):
        return self.cost + self.h * 1

    def __str__(self):
        return "x: %d,y: %d,degree: %d" % (self.x, self.y, self.degree)
