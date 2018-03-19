# -*- encoding: utf-8 -*-


def passenger(data, event, person):
    distance = event.get('distance')
    for train in data:
        cars = train.get('cars')
        for i, car in enumerate(cars):
            if person in car.get('people'):
                if len(cars) > abs(distance):
                    cars[i+distance]['people'].append(person)
                    car['people'].remove(person)
                    return True
                else:
                    return False
    return False


def trains(data, event):
    train_from = event.get('train_from')
    train_to = event.get('train_to')
    count = event.get('cars')
    train_from_index = None
    train_to_index = None
    for i, train in enumerate(data):
        name = train['name']
        if name == train_from:
            train_from_index = i
            if count > len(data[train_from_index]['cars']):
                return False
        if name == train_to:
            train_to_index = i
    if train_from_index is not None and train_to_index is not None:
        for idx in range(count):
            data[train_to_index]['cars'].append(data[train_from_index]['cars'].pop(-count+idx))
    else:
        return False
    return True


def process(data, events, res):
    for event in events:
        person = event.get('passenger')
        if person and event.get('type') == 'walk' and passenger(data, event, person):
            continue
        elif event.get('type') == 'switch' and trains(data, event):
            continue
        else:
            return -1
    for train in data:
        for car in train['cars']:
            if res == car.get('name'):
                return len(car['people'])
    return -1
