def lives_in_denver(screen):
    '''
    Household lives in the Denver County
    '''
    return screen.county == 'Denver County'


def helpkitchen_zipcode(screen):
    '''
    Lives in an Aurora zipcode
    '''
    zipcodes = [
        '80010',
        '80011',
        '80012',
        '80013',
        '80014',
        '80015',
        '80016',
        '80017',
        '80018',
        '80019',
        '80045',
        '80102',
        '80112',
        '80137',
        '80138',
        '80230',
        '80231',
        '80238',
        '80247',
        '80249',
    ]
    return screen.zipcode in zipcodes
