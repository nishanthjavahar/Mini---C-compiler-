int age;
int citizen;
int eligible;
int attempts;

int history[5];

age = 20;

citizen = 1;

attempts = 0;

eligible = 0;

if (age >= 18) {

    print(age);
}

if (citizen == 1) {

    print(citizen);
}

if (age >= 18) {

    eligible = 1;

    print(eligible);
}

while (attempts < 3) {

    attempts = attempts + 1;

    print(attempts);
}

eligible = eligible + attempts;

print(eligible);