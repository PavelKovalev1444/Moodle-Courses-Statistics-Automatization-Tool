import numpy as np
import matplotlib.pyplot as plt


x_values = [
  1, 
  2, 
  3, 
  4, 
  5, 
  6, 
  7
]
# time measuring
'''
y_values = [
  0.6345497710062773, 
  1.041182225002558, 
  1.1810535679978784,
  1.3305010795593262,
  1.417639970779419,
  1.6388561725616455,
  2.0546393394470215,
]
'''
# memory measuring
y_values = [
  81.2, 
  81.3, 
  81.6,
  81.4,
  81.2,
  82.1,
  81.9
]
 
x_labels = [
  'Онлайн-курсы, шт.',
]

y_labels = [
  'Время работы, с',
  'Затраченная память, МБ'
]

fig, ax = plt.subplots(figsize=(10, 10))
ax.plot(x_values, y_values, 'b', marker="o", mec="r", mfc="r")

for i in range(len(x_values)):
    ax.plot([x_values[i], x_values[i]], [0, y_values[i]], 'b', linestyle='dashed')
    ax.plot([0, x_values[i]], [y_values[i], y_values[i]], 'b', linestyle='dashed')

ax.grid()
#ax.set_title('График зависимости времени работы')
ax.set_ylabel(y_labels[1])
ax.set_xlabel(x_labels[0])
ax.legend()
ax.set_xlim(xmin=0, xmax=x_values[-1] + 1)
ax.set_ylim(ymin=0, ymax=y_values[-1] + 1)
 
plt.show()