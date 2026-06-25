import time

def countdown(my_time):
    for x in range(my_time, 0, -1):
        seconds = x % 60
        minutes = int(x / 60) % 60
        hours = int(x / 3600)
        print(f"{hours:02}:{minutes:02}:{seconds:02}")
        time.sleep(1)
    print("Time's up! Take a break!")

def countdown_break(break_time):
    for x in range(break_time, 0, -1):
        seconds = x % 60
        minutes = int(x / 60) % 60
        hours = int(x / 3600)
        print(f"{hours:02}:{minutes:02}:{seconds:02}")
        time.sleep(1)
    print("Break's over! Get back to work!")


print("Welcome to Lock In Arc!")

option = int(input("Would you like a custom or pomodoro timer? (1 for custom, 2 for pomodoro): "))
cycles=int(input("How many cycles would you like to complete? "))

for i in range(cycles):
    if option == 1:
        focus_time = int(input("Enter the focus time in minutes: "))
        break_time = int(input("Enter the break time in minutes: "))
    else:
        focus_time = 25
        break_time = 5

countdown(focus_time * 60)
countdown_break(break_time * 60)



    
       


    
 
