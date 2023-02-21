def income(income, max_income):
    '''
    Household makes ${income} per month which must be less than ${max_income}
    '''
    return (
        'Household makes',
        f' ${round(income)} ',
        'per month which must be less than',
        f' ${round(max_income)}'
    )


def child(min_age=0, max_age=18):
    '''
    Must have a child between the ages of {min_age} and {max_age}
    '''
    return (
        'Must have a child between the ages of',
        f' {min_age} ',
        'and',
        f' {max_age}'
    )


def adult(min_age, max_age):
    '''
    Someone in the household must be between the ages of {min_age} and {max_age}
    '''
    return (
        'Someone in the household must be between the ages of',
        f' {min_age} ',
        'and',
        f' {max_age}'
    )


def must_have_benefit(benefit_name):
    '''
    Household must have {benefit_name}
    '''
    return (
        'Household must have',
        f' {benefit_name}'
    )


def must_not_have_benefit(benefit_name):
    '''
    Household must not have {benefit_name}
    '''
    return (
        'Household must not have',
        f' {benefit_name}'
    )


def location():
    '''
    Must live in an eligible location
    '''
    return (
        'Must live in an eligible location',
    )


def has_disability():
    '''
    Someone in the household must have a disability
    '''
    return (
        'Someone in the household must have a disability'
    )


def has_no_insturance():
    '''
    Someone in the household must not have health insurance
    '''
    return (
        'Someone in the household must not have health insurance'
    )
