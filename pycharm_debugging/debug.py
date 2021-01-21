import random

def gen_random(upper):
    r = random.randint(1,upper)
    return r

def main():
    run = True
    num1 = gen_random(10)
    num2 = gen_random(10)
    results = num1 * num2
    while run:
        ans = input(f'what is the {str(num1)} x {str(num2)}?')

        if ans.isdigit():
            if int(ans) == results:
                print('correct')
                run = False
            else:
                print('incorrect try again')
        else:
            print('answer must be a pos number, try again ')

if __name__ == '__main__':
    for _ in range(10):
        main()