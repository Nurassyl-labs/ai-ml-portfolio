import random

secret = random.randint(1, 100)
print('''猜数游戏！
      我想了一个1-100的整数，你最多可以猜6次, 
      看看能猜出来吗？''')
tries = 1
while tries <= 6:
      guess = int(input("1-100的整数，第%d次猜，请输入："%(tries,)))
      if guess == secret: 
            print("Поздравляю, вы угадали с %d попытки! \n число: %d!" %(tries, secret))
            break
      elif guess > secret:
            print("Ты слишком много взял")
      else: 
            print("извини н о слишком мало")
      tries+=1
else: 
      print("как так не смог?")

      