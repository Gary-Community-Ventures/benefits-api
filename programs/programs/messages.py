from django.utils.translation import gettext_noop as _


def income(income, max_income):
    '''
    Household makes ${income} per month which must be less than ${max_income}
    '''
    return (
        _('Household makes'),
        f' ${round(income)} ',
        _('per month which must be less than'),
        f' ${round(max_income)}'
    )


def assets(asset_limit):
    '''
    Household resources must not exceed ${asset_limit}
    '''
    return (
        _('Household resources must not exceed'),
        f' ${round(asset_limit)}'
    )


def child(min_age=0, max_age=18):
    '''
    Must have a child between the ages of {min_age} and {max_age}
    '''
    return (
        _('Must have a child between the ages of'),
        f' {min_age} ',
        _('and'),
        f' {max_age}'
    )


def adult(min_age, max_age):
    '''
    Someone in the household must be between the ages of {min_age} and {max_age}
    '''
    return (
        _('Someone in the household must be between the ages of'),
        f' {min_age} ',
        _('and'),
        f' {max_age}'
    )


def older_than(min_age):
    '''
    Someone in the household must be at least {min_age} years old
    '''
    return (
        _('Someone in the household must be at least'),
        f' {min_age} ',
        _('years old')
    )


def must_have_benefit(benefit_name):
    '''
    Household must have {benefit_name}
    '''
    return (
        _('Household must have'),
        f' {benefit_name}'
    )


def must_not_have_benefit(benefit_name):
    '''
    Household must not have {benefit_name}
    '''
    return (
        _('Household must have'),
        f' {benefit_name}'
    )


def location():
    '''
    Must live in an eligible location
    '''
    return (
        _('Must live in an eligible location'),
    )


def has_disability():
    '''
    Someone in the household must have a disability
    '''
    return (
        _('Someone in the household must have a disability')
    )


def has_no_insturance():
    '''
    Someone in the household must not have health insurance
    '''
    return (
        _('Someone in the household must not have health insurance')
    )
