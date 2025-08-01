id1 = {}
id_cnt = 0

# dat[사용자ID][요일]
dat = [[0] * 100 for _ in range(100)]
points = [0] * 100
grade = [0] * 100
names = [''] * 100
wed = [0] * 100
weeken = [0] * 100

def input2(w, wk):
    global id_cnt

    if w not in id1:
        id_cnt += 1
        id1[w] = id_cnt
        names[id_cnt] = w

    id2 = id1[w]

    add_point = 0
    index = 0

    if wk == "monday":
        index = 0
        add_point += 1
    elif wk == "tuesday":
        index = 1
        add_point += 1
    elif wk == "wednesday":
        index = 2
        add_point += 3
        wed[id2] += 1
    elif wk == "thursday":
        index = 3
        add_point += 1
    elif wk == "friday":
        index = 4
        add_point += 1
    elif wk == "saturday":
        index = 5
        add_point += 2
        weeken[id2] += 1
    elif wk == "sunday":
        index = 6
        add_point += 2
        weeken[id2] += 1

    dat[id2][index] += 1
    points[id2] += add_point

def input_file():
    try:
        with open("attendance_weekday_500.txt", encoding='utf-8') as f:
            for _ in range(500):
                line = f.readline()
                if not line:
                    break
                parts = line.strip().split()
                if len(parts) == 2:
                    input2(parts[0], parts[1])

        for i in range(1, id_cnt + 1):
            if dat[i][3] > 9:
                points[i] += 10
            if dat[i][5] + dat[i][6] > 9:
                points[i] += 10

            if points[i] >= 50:
                grade[i] = 1
            elif points[i] >= 30:
                grade[i] = 2
            else:
                grade[i] = 0

            print(f"NAME : {names[i]}, POINT : {points[i]}, GRADE : ", end="")
            if grade[i] == 1:
                print("GOLD")
            elif grade[i] == 2:
                print("SILVER")
            else:
                print("NORMAL")

        print("\nRemoved player")
        print("==============")
        for i in range(1, id_cnt + 1):
            if grade[i] not in (1, 2) and wed[i] == 0 and weeken[i] == 0:
                print(names[i])

    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    input_file()