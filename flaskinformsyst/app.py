import base64
import math
from io import BytesIO

import numpy as np
from flask import Flask, render_template, request, url_for, redirect
from matplotlib import pyplot as plt

import basic_model

app = Flask(__name__)

var_names = ['остаток денежных средств',
             'выручка',
             'прибыль',
             'активы',
             'численность',
             'конкурентоспособность',
             'объем продаж в натуральном выражении',
             'инновационность',
             'известность бренда',
             'материалоемкость',
             'количество ремонтов',
             'износ оборудования',
             'налоги в бюджет',
             'социальная сфера',
             'экологичность']

keys = ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11", "L12", "L13", "L14", "L15"]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_values = request.form.getlist('values[]')
        input_min_values = request.form.getlist('min_values[]')
        input_f_args = request.form.getlist('f_args[]')
        input_q_args = request.form.getlist('q_args[]')
        return redirect(url_for('result', values=input_values, min_values=input_min_values, f_args=input_f_args, q_args=input_q_args))
    return render_template("index.html", var_names=var_names)


@app.route('/result')
def result():
    print(request.args.getlist('values'))
    print(request.args.getlist('f_args'))
    print(request.args.getlist('q_args'))
    values = list(map(str2float, request.args.getlist('values')))
    min_values = list(map(str2float, request.args.getlist('min_values')))
    f_args = list(map(str2float, request.args.getlist('f_args')))
    q_args = list(map(str2float, request.args.getlist('q_args')))
    n = 0
    f_res = []
    tmp = []
    q_res = []
    tmq = []
    for arg in f_args:
        tmp.append(arg)
        if n == 3:
            f_res.append(tmp)
            tmp = []
        n += 1
        n %= 4

    for arg in q_args:
        tmq.append(arg)
        if n == 3:
            q_res.append(tmq)
            tmq = []
        n += 1
        n %= 4

    basic_model.f_ind = f_res
    basic_model.q_ind = q_res
    basic_model.map = {basic_model.keys[i]: values[i] for i in range(len(basic_model.keys))}

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_position([0.05, 0.25, 0.3, 0.8])
    ax.set_aspect('equal')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    solution = basic_model.solve(list(map(str2float, request.args.getlist('values'))))

    for i in range(15):
        ax.plot(solution.t, solution.y[i], label=f'y{i + 1}')

    ax.plot([1, 1])
    ax.legend(var_names, fontsize=10, bbox_to_anchor=(1.03, 1), loc='upper left')  # , prop=FontProperties(size=6)
    # ax.set_aspect('equal')

    # fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")

    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    return render_template("result.html", data=data)


@app.route("/polar_plot")
def polar_plot():
    values = list(map(str2float, request.args.getlist('values')))
    min_values = list(map(str2float, request.args.getlist('min_values')))
    f_args = list(map(str2float, request.args.getlist('f_args')))
    q_args = list(map(str2float, request.args.getlist('q_args')))

    # Формирование списков f_res и q_res
    n = 0
    f_res = []
    tmp = []
    q_res = []
    tmq = []

    for arg in f_args:
        tmp.append(arg)
        if n == 3:
            f_res.append(tmp)
            tmp = []
        n += 1
        n %= 4

    for arg in q_args:
        tmq.append(arg)
        if n == 3:
            q_res.append(tmq)
            tmq = []
        n += 1
        n %= 4

    basic_model.f_ind = f_res
    basic_model.q_ind = q_res
    basic_model.map = {basic_model.keys[i]: values[i] for i in range(len(basic_model.keys))}

    images = []  # Список для хранения изображений

    # Определите angles для 15 переменных
    angles = np.linspace(0, 2 * np.pi, len(min_values), endpoint=False)

    for t in [0, 0.25, 0.5, 0.75, 1]:
        fig = plt.figure(dpi=200)
        ax = fig.add_subplot(projection='polar')
        ax.set_aspect('equal')

        initial_conditions = [value * (1 + t) for value in values]  # Изменение начальных условий
        solution = basic_model.solve(initial_conditions)

        r = np.deg2rad(np.arange(0, 360, 360 / 15))
        num_time_steps = len(solution.y[0])
        theta_index = int(t * (num_time_steps - 1))  # Убедитесь, что индекс корректен
        theta = [solution.y[i][theta_index] for i in range(len(solution.y))]

        ax.plot(r, theta)  # Построение графика с текущими значениями

        # Проверка значений min_values
        print("min_values:", min_values)  # Вывод значений для отладки
        print("angles:", angles)  # Вывод углов для отладки

        ax.plot(angles, min_values, 'r', linewidth=2)  # Красная линия для минимальных значений
        ax.fill(angles, min_values, 'r', alpha=0.1)  # Закрашивание области под линией минимальных значений
        ax.set_xticks(r, fontsize=4)
        ax.set_xticklabels(basic_model.keys, fontsize=12)

        buf = BytesIO()
        fig.savefig(buf, format="png")
        images.append(base64.b64encode(buf.getbuffer()).decode("ascii"))

    return render_template("polar.html", images=images)  # Передать список изображений в шаблон

# @app.route("/polar_plot")
# def polar_plot():
#     values = list(map(str2float, request.args.getlist('values')))
#     min_values = list(map(str2float, request.args.getlist('min_values')))
#     f_args = list(map(str2float, request.args.getlist('f_args')))
#     q_args = list(map(str2float, request.args.getlist('q_args')))
#     n = 0
#     f_res = []
#     tmp = []
#     q_res = []
#     tmq = []
#
#     for arg in f_args:
#         tmp.append(arg)
#         if n == 3:
#             f_res.append(tmp)
#             tmp = []
#         n += 1
#         n %= 4
#
#     for arg in q_args:
#         tmq.append(arg)
#         if n == 3:
#             q_res.append(tmq)
#             tmq = []
#         n += 1
#         n %= 4
#
#     basic_model.f_ind = f_res
#     basic_model.q_ind = q_res
#     basic_model.map = {basic_model.keys[i]: values[i] for i in range(len(basic_model.keys))}
#
#     images = []  # Список для хранения изображений
#
#     for t in [0, 0.25, 0.5, 0.75, 1]:
#         fig = plt.figure(dpi=200)
#         ax = fig.add_subplot(projection='polar')
#         ax.set_aspect('equal')
#
#         initial_conditions = [value * (1 + t) for value in values]  # Изменение начальных условий
#         solution = basic_model.solve(initial_conditions)
#
#         r = np.deg2rad(np.arange(0, 360, 360 / 15))
#         num_time_steps = len(solution.y[0])
#         theta_index = int(t * (num_time_steps - 1))  # Убедитесь, что индекс корректен
#         theta = [solution.y[i][theta_index] for i in range(len(solution.y))]
#
#         ax.plot(r, theta)
#         ax.plot(angles, min_values, 'r', linewidth=2)
#         ax.fill(angles, min_values, 'r', alpha=0.1)
#         ax.set_xticks(r, fontsize=9)
#         ax.set_xticklabels(keys, fontsize=12)
#
#         buf = BytesIO()
#         fig.savefig(buf, format="png")
#         images.append(base64.b64encode(buf.getbuffer()).decode("ascii"))
#
#     return render_template("polar.html", images=images)  # Передать список изображений в шаблон


@app.route("/gr", methods=["POST"])
def gr():
    input_values = request.form.getlist('values[]')
    input_min_values = request.form.getlist('min_values[]')
    input_f_args = request.form.getlist('f_args[]')
    input_q_args = request.form.getlist('q_args[]')
    action = request.form.get('action')
    if action == "graphic":
        return redirect(url_for('result', values=input_values, f_args=input_f_args, q_args=input_q_args))
    elif action == "polar_diagram":
        return redirect(url_for('polar_plot', values=input_values, min_values=input_min_values, f_args=input_f_args, q_args=input_q_args))
    else:
        return redirect('/')


def str2float(value):
    return float(value.replace(",", ".")) if value != "" else 0.


if __name__ == '__main__':
    app.run()
