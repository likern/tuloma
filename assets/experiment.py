from los import profile_los

# Измените координаты или высоты и запустите снова.
x_a, x_b = 0, 80
h_a, h_b = 0, 0

result = profile_los(x_a, x_b, h_a, h_b)
print(result)
