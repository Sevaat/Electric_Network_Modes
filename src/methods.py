from abc import ABC

from src.numerical_methods.newton_method.newton_method import NewtonMethod


class Methods(ABC):
    @staticmethod
    def newton_method() -> None:
        """
        Рассчитать режим методом Ньютона
        :return:
        """
        nm = NewtonMethod()
        nm.run()