from .base import ConfigurationData
from screener.models import WhiteLabel


# TODO: Update NC configuration
class NcConfigurationData(ConfigurationData):
    @classmethod
    def get_white_label(self) -> WhiteLabel:
        return WhiteLabel.objects.get(code="nc")

    public_charge_rule = {"link": "https://www.ncjustice.org/publications/public-charge-the-law-has-changed/"}

    more_help_options = {
        "moreHelpOptions": [
            {
                "name": {
                    "_default_message": "2-1-1 North Carolina",
                    "_label": "moreHelp.resource_name1",
                },
                "link": "https://nc211.org/",
                "phone": {
                    "_default_message": "Dial 2-1-1 or 866.760.6489",
                    "_label": "moreHelp.resource_phone1",
                },
            },
            {
                "name": {
                    "_default_message": "NCCARE360",
                    "_label": "moreHelp.resource_name2",
                },
                "description": {
                    "_default_message": "NCCARE360 is the first statewide coordinated care network that better connects individuals to local services and resources. NCCARE360 provides a solution to a fragmented health and human services system by connecting providers and organizations across sectors in a shared technology network. In the NCCARE360 network, providers can electronically connect individuals and families who have unmet social needs to community resources. NCCARE360 also allows for easy feedback and follow-up to help close the care loop for individuals and families seeking help.",
                    "_label": "moreHelp.resource_description1",
                },
                "link": "https://nccare360.org/request-assistance/",
            },
        ]
    }

    acute_condition_options = {
        "food": {
            "icon": {"_icon": "Food", "_classname": "option-card-icon"},
            "text": {
                "_label": "acuteConditionOptions.food",
                "_default_message": "Food or groceries",
            },
        },
        "babySupplies": {
            "icon": {"_icon": "Baby_supplies", "_classname": "option-card-icon"},
            "text": {
                "_label": "acuteConditionOptions.babySupplies",
                "_default_message": "Diapers and other baby supplies",
            },
        },
        "housing": {
            "icon": {"_icon": "Housing", "_classname": "option-card-icon"},
            "text": {
                "_label": "acuteConditionOptions.housing",
                "_default_message": "Help with managing your mortgage, rent, or utilities",
            },
        },
        "support": {
            "icon": {"_icon": "Support", "_classname": "option-card-icon"},
            "text": {
                "_label": "acuteConditionOptions.support",
                "_default_message": "A challenge you or your child would like to talk about",
            },
        },
        "childDevelopment": {
            "icon": {"_icon": "Child_development", "_classname": "option-card-icon"},
            "text": {
                "_label": "acuteConditionOptions.childDevelopment",
                "_default_message": "Concern about your child's development",
            },
        },
        "familyPlanning": {
            "icon": {"_icon": "Family_planning", "_classname": "option-card-icon"},
            "text": {
                "_label": "acuteConditionOptions.familyPlanning",
                "_default_message": "Family planning or birth control",
            },
        },
        "jobResources": {
            "icon": {"_icon": "Job_resources", "_classname": "option-card-icon"},
            "text": {
                "_label": "acuteConditionOptions.jobResources",
                "_default_message": "Finding a job",
            },
        },
        "dentalCare": {
            "icon": {"_icon": "Dental_care", "_classname": "option-card-icon"},
            "text": {
                "_label": "acuteConditionOptions.dentalCare",
                "_default_message": "Low-cost dental care",
            },
        },
        "legalServices": {
            "icon": {"_icon": "Legal_services", "_classname": "option-card-icon"},
            "text": {
                "_label": "acuteConditionOptions.legalServices",
                "_default_message": "Free or low-cost help with civil legal needs or IDs",
            },
        },
    }

    sign_up_options = {
        "sendUpdates": {
            "_label": "signUpOptions.sendUpdates",
            "_default_message": "Please notify me when new benefits become available to me that I am likely eligible for based on the information I have provided.",
        },
        "sendOffers": {
            "_label": "signUpOptions.sendOffers",
            "_default_message": "Please notify me when there are paid opportunities to provide feedback on this screener.",
        },
    }

    relationship_options = {
        "child": {"_label": "relationshipOptions.child", "_default_message": "Child"},
        "fosterChild": {
            "_label": "relationshipOptions.fosterChildOrKinshipChild",
            "_default_message": "Foster Child / Kinship Care",
        },
        "stepChild": {
            "_label": "relationshipOptions.stepChild",
            "_default_message": "Step-child",
        },
        "grandChild": {
            "_label": "relationshipOptions.grandChild",
            "_default_message": "Grandchild",
        },
        "spouse": {
            "_label": "relationshipOptions.spouse",
            "_default_message": "Spouse",
        },
        "parent": {
            "_label": "relationshipOptions.parent",
            "_default_message": "Parent",
        },
        "fosterParent": {
            "_label": "relationshipOptions.fosterParent",
            "_default_message": "Foster Parent",
        },
        "stepParent": {
            "_label": "relationshipOptions.stepParent",
            "_default_message": "Step-parent",
        },
        "grandParent": {
            "_label": "relationshipOptions.grandParent",
            "_default_message": "Grandparent",
        },
        "sisterOrBrother": {
            "_label": "relationshipOptions.sisterOrBrother",
            "_default_message": "Sister/Brother",
        },
        "stepSisterOrBrother": {
            "_label": "relationshipOptions.stepSisterOrBrother",
            "_default_message": "Step-sister/Step-brother",
        },
        "boyfriendOrGirlfriend": {
            "_label": "relationshipOptions.boyfriendOrGirlfriend",
            "_default_message": "Boyfriend/Girlfriend",
        },
        "domesticPartner": {
            "_label": "relationshipOptions.domesticPartner",
            "_default_message": "Domestic Partner",
        },
        "unrelated": {
            "_label": "relationshipOptions.unrelated",
            "_default_message": "Unrelated",
        },
        "relatedOther": {
            "_label": "relationshipOptions.relatedOther",
            "_default_message": "Related in some other way",
        },
    }

    referral_options = {
        "211co": "2-1-1 North Carolina",
        "testOrProspect": {
            "_label": "referralOptions.testOrProspect",
            "_default_message": "Test / Prospective Partner",
        },
        "searchEngine": {
            "_label": "referralOptions.searchEngine",
            "_default_message": "Google or other search engine",
        },
        "socialMedia": {
            "_label": "referralOptions.socialMedia",
            "_default_message": "Social Media",
        },
        "other": {"_label": "referralOptions.other", "_default_message": "Other"},
        "nariahWay": {
            "_label": "referralOptions.nw",
            "_default_message": "Nariah's Way",
        },
        "ncchwa": {
            "_label": "referralOptions.NCCHWA",
            "_default_message": "North Carolina Community Health Worker Association (NCCHWA)",
        },
        "rcp": {
            "_label": "referralOptions.rcp",
            "_default_message": "Refugee Community Partnership",
        },
        "ruralHealthGroup": {
            "_label": "referralOptions.ruralHealthGroup",
            "_default_message": "Rural Health Group",
        },
        "unidx": {
            "_label": "referralOptions.unidxWNC",
            "_default_message": "Unidx WNC",
        },
        "downHome": {
            "_label": "referralOptions.weAreDownHome",
            "_default_message": "We Are Down Home",
        },
        "blueprint": {
            "_label": "referralOptions.blueprint",
            "_default_message": "Blueprint NC",
        },
        "elRefugio": {
            "_label": "referralOptions.elRefugio",
            "_default_message": "El Refugio",
        },
        "fiel": {
            "_label": "referralOptions.fiel",
            "_default_message": "Duke Project FIEL-NC (FIEL-NC)",
        },
        "felp": {
            "_label": "referralOptions.felp",
            "_default_message": "Future Endeavors Life Program (FELP)",
        },
        "mda": {
            "_label": "referralOptions.mda",
            "_default_message": "Montagnard Dega Association",
        },
        "mgm": {
            "_label": "referralOptions.mgm",
            "_default_message": "Mundeke Gospel Mission",
        },
    }

    language_options = {
        "en-us": "English",
        "es": "Espau00f1ol",
        "vi": "Tiu1ebfng Viu1ec7t",
        "fr": "Franu00e7ais",
        "am": "u12a0u121bu122du129b",
        "so": "Soomaali",
        "ru": "u0420u0443u0441u0441u043au0438u0439",
        "ne": "u0928u0947u092au093eu0932u0940",
        "my": "u1019u103cu1014u103au1019u102cu1018u102cu101eu102cu1005u1000u102cu1038",
        "zh": "u4e2du6587",
        "ar": "u0639u0631u0628u064a",
    }

    income_options = {
        "wages": {
            "_label": "incomeOptions.wages",
            "_default_message": "Wages, salaries, tips",
        },
        "selfEmployment": {
            "_label": "incomeOptions.selfEmployment",
            "_default_message": "Income from freelance, independent contractor, or self-employment work",
        },
        "sSDisability": {
            "_label": "incomeOptions.sSDisability",
            "_default_message": "Social Security Disability Benefits",
        },
        "sSRetirement": {
            "_label": "incomeOptions.sSRetirement",
            "_default_message": "Social Security Retirement Benefits",
        },
        "sSI": {
            "_label": "incomeOptions.sSI",
            "_default_message": "Supplemental Security Income (SSI)",
        },
        "childSupport": {
            "_label": "incomeOptions.childSupport",
            "_default_message": "Child Support (Received)",
        },
        "pension": {
            "_label": "incomeOptions.pension",
            "_default_message": "Military, Government, or Private Pension",
        },
        "veteran": {
            "_label": "incomeOptions.veteran",
            "_default_message": "Veteran's Pension or Benefits",
        },
        "sSSurvivor": {
            "_label": "incomeOptions.sSSurvivor",
            "_default_message": "Social Security Survivor's Benefits (Widow/Widower)",
        },
        "unemployment": {
            "_label": "incomeOptions.unemployment",
            "_default_message": "Unemployment Benefits",
        },
        "sSDependent": {
            "_label": "incomeOptions.sSDependent",
            "_default_message": "Social Security Dependent Benefits (retirement, disability, or survivors)",
        },
        "cashAssistance": {
            "_label": "incomeOptions.cashAssistance",
            "_default_message": "Cash Assistance Grant",
        },
        "gifts": {
            "_label": "incomeOptions.gifts",
            "_default_message": "Gifts/Contributions (Received)",
        },
        "investment": {
            "_label": "incomeOptions.investment",
            "_default_message": "Investment Income (interest, dividends, and profit from selling stocks)",
        },
        "rental": {
            "_label": "incomeOptions.rental",
            "_default_message": "Rental Income",
        },
        "alimony": {
            "_label": "incomeOptions.alimony",
            "_default_message": "Alimony (Received)",
        },
        "deferredComp": {
            "_label": "incomeOptions.deferredComp",
            "_default_message": "Withdrawals from Deferred Compensation (IRA, Keogh, etc.)",
        },
        "workersComp": {
            "_label": "incomeOptions.workersComp",
            "_default_message": "Worker's Compensation",
        },
        "boarder": {
            "_label": "incomeOptions.boarder",
            "_default_message": "Boarder or Lodger",
        },
    }

    health_insurance_options = {
        "you": {
            "none": {
                "icon": {"_icon": "None", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.none-dont-know-I",
                    "_default_message": "I don't have or know if I have health insurance",
                },
            },
            "employer": {
                "icon": {"_icon": "Employer", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.employer",
                    "_default_message": "Employer-provided health insurance",
                },
            },
            "private": {
                "icon": {"_icon": "PrivateInsurance", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.private",
                    "_default_message": "Private (non-employer) health insurance",
                },
            },
            "medicaid": {
                "icon": {"_icon": "Medicaid", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.medicaid",
                    "_default_message": "Health First Colorado (Full Medicaid)",
                },
            },
            "medicare": {
                "icon": {"_icon": "Medicare", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.medicare",
                    "_default_message": "Medicare",
                },
            },
            "emergency_medicaid": {
                "icon": {
                    "_icon": "Emergency_medicaid",
                    "_classname": "option-card-icon",
                },
                "text": {
                    "_label": "healthInsuranceOptions.emergency_medicaid",
                    "_default_message": "Emergency Medicaid / Reproductive Health",
                },
            },
            "family_planning": {
                "icon": {"_icon": "Family_planning", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.family_planning",
                    "_default_message": "Family Planning Limited Medicaid",
                },
            },
            "va": {
                "icon": {"_icon": "VA", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.va",
                    "_default_message": "VA health care benefits",
                },
            },
        },
        "them": {
            "none": {
                "icon": {"_icon": "None", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.none-dont-know-they",
                    "_default_message": "They don't have or know if they have health insurance",
                },
            },
            "employer": {
                "icon": {"_icon": "Employer", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.employer",
                    "_default_message": "Employer-provided health insurance",
                },
            },
            "private": {
                "icon": {"_icon": "PrivateInsurance", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.private",
                    "_default_message": "Private (non-employer) health insurance",
                },
            },
            "medicaid": {
                "icon": {"_icon": "Medicaid", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.medicaid",
                    "_default_message": "Health First Colorado (Full Medicaid)",
                },
            },
            "medicare": {
                "icon": {"_icon": "Medicare", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.medicare",
                    "_default_message": "Medicare",
                },
            },
            "emergency_medicaid": {
                "icon": {
                    "_icon": "Emergency_medicaid",
                    "_classname": "option-card-icon",
                },
                "text": {
                    "_label": "healthInsuranceOptions.emergency_medicaid",
                    "_default_message": "Emergency Medicaid / Reproductive Health",
                },
            },
            "family_planning": {
                "icon": {"_icon": "Family_planning", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.family_planning",
                    "_default_message": "Family Planning Limited Medicaid",
                },
            },
            "va": {
                "icon": {"_icon": "VA", "_classname": "option-card-icon"},
                "text": {
                    "_label": "healthInsuranceOptions.va",
                    "_default_message": "VA health care benefits",
                },
            },
        },
    }

    frequency_options = {
        "weekly": {
            "_label": "frequencyOptions.weekly",
            "_default_message": "every week",
        },
        "biweekly": {
            "_label": "frequencyOptions.biweekly",
            "_default_message": "every 2 weeks",
        },
        "semimonthly": {
            "_label": "frequencyOptions.semimonthly",
            "_default_message": "twice a month",
        },
        "monthly": {
            "_label": "frequencyOptions.monthly",
            "_default_message": "every month",
        },
        "yearly": {"_label": "frequencyOptions.yearly", "_default_message": "yearly"},
        "hourly": {"_label": "frequencyOptions.hourly", "_default_message": "hourly"},
    }

    expense_options = {
        "rent": {"_label": "expenseOptions.rent", "_default_message": "Rent"},
        "telephone": {
            "_label": "expenseOptions.telephone",
            "_default_message": "Telephone",
        },
        "internet": {
            "_label": "expenseOptions.internet",
            "_default_message": "Internet",
        },
        "otherUtilities": {
            "_label": "expenseOptions.otherUtilities",
            "_default_message": "Other Utilities",
        },
        "heating": {"_label": "expenseOptions.heating", "_default_message": "Heating"},
        "creditCard": {
            "_label": "expenseOptions.creditCard",
            "_default_message": "Credit Card Debt",
        },
        "mortgage": {
            "_label": "expenseOptions.mortgage",
            "_default_message": "Mortgage",
        },
        "medical": {
            "_label": "expenseOptions.medical",
            "_default_message": "Medical Insurance Premium &/or Bills",
        },
        "personalLoan": {
            "_label": "expenseOptions.personalLoan",
            "_default_message": "Personal Loan",
        },
        "studentLoans": {
            "_label": "expenseOptions.studentLoans",
            "_default_message": "Student Loans",
        },
        "cooling": {"_label": "expenseOptions.cooling", "_default_message": "Cooling"},
        "childCare": {
            "_label": "expenseOptions.childCare",
            "_default_message": "Child Care",
        },
        "childSupport": {
            "_label": "expenseOptions.childSupport",
            "_default_message": "Child Support (Paid)",
        },
        "dependentCare": {
            "_label": "expenseOptions.dependentCare",
            "_default_message": "Dependent Care",
        },
    }

    condition_options = {
        "you": {
            "student": {
                "icon": {"_icon": "Student", "_classname": "option-card-icon"},
                "text": {
                    "_label": "conditionOptions.student",
                    "_default_message": "Student at a college, university, or other post-secondary institution like a job-training program",
                },
            },
            "pregnant": {
                "icon": {"_icon": "Pregnant", "_classname": "option-card-icon"},
                "text": {
                    "_label": "conditionOptions.pregnant",
                    "_default_message": "Pregnant",
                },
            },
            "blindOrVisuallyImpaired": {
                "icon": {
                    "_icon": "BlindOrVisuallyImpaired",
                    "_classname": "option-card-icon",
                },
                "text": {
                    "_label": "conditionOptions.blindOrVisuallyImpaired",
                    "_default_message": "Blind or visually impaired",
                },
            },
            "disabled": {
                "icon": {"_icon": "Disabled", "_classname": "option-card-icon"},
                "text": {
                    "_label": "conditionOptions.disabled",
                    "_default_message": "Have any disabilities that make you unable to work now or in the future",
                },
            },
            "longTermDisability": {
                "icon": {
                    "_icon": "LongTermDisability",
                    "_classname": "option-card-icon",
                },
                "text": {
                    "_label": "conditionOptions.longTermDisability",
                    "_default_message": "Any medical or developmental condition that has lasted, or is expected to last, more than 12 months",
                },
            },
        },
        "them": {
            "student": {
                "icon": {"_icon": "Student", "_classname": "option-card-icon"},
                "text": {
                    "_label": "conditionOptions.student",
                    "_default_message": "Student at a college, university, or other post-secondary institution like a job-training program",
                },
            },
            "pregnant": {
                "icon": {"_icon": "Pregnant", "_classname": "option-card-icon"},
                "text": {
                    "_label": "conditionOptions.pregnant",
                    "_default_message": "Pregnant",
                },
            },
            "blindOrVisuallyImpaired": {
                "icon": {
                    "_icon": "BlindOrVisuallyImpaired",
                    "_classname": "option-card-icon",
                },
                "text": {
                    "_label": "conditionOptions.blindOrVisuallyImpaired",
                    "_default_message": "Blind or visually impaired",
                },
            },
            "disabled": {
                "icon": {"_icon": "Disabled", "_classname": "option-card-icon"},
                "text": {
                    "_label": "conditionOptions.disabled",
                    "_default_message": "Have any disabilities that make you unable to work now or in the future",
                },
            },
            "longTermDisability": {
                "icon": {
                    "_icon": "LongTermDisability",
                    "_classname": "option-card-icon",
                },
                "text": {
                    "_label": "conditionOptions.longTermDisability",
                    "_default_message": "Any medical or developmental condition that has lasted, or is expected to last, more than 12 months",
                },
            },
        },
    }

    counties_by_zipcode = {
        "27006": {"Davie County": "Davie County"},
        "27007": {"Surry County": "Surry County"},
        "27009": {"Forsyth County": "Forsyth County", "Stokes County": "Stokes County"},
        "27010": {"Forsyth County": "Forsyth County"},
        "27011": {"Yadkin County": "Yadkin County"},
        "27012": {
            "Forsyth County": "Forsyth County",
            "Davidson County": "Davidson County",
        },
        "27013": {"Rowan County": "Rowan County", "Iredell County": "Iredell County"},
        "27014": {"Davie County": "Davie County"},
        "27016": {"Stokes County": "Stokes County"},
        "27017": {"Surry County": "Surry County"},
        "27018": {"Yadkin County": "Yadkin County"},
        "27019": {"Stokes County": "Stokes County", "Forsyth County": "Forsyth County"},
        "27020": {
            "Yadkin County": "Yadkin County",
            "Iredell County": "Iredell County",
            "Wilkes County": "Wilkes County",
        },
        "27021": {"Stokes County": "Stokes County", "Forsyth County": "Forsyth County"},
        "27022": {"Stokes County": "Stokes County"},
        "27023": {"Forsyth County": "Forsyth County"},
        "27024": {"Surry County": "Surry County"},
        "27025": {
            "Rockingham County": "Rockingham County",
            "Stokes County": "Stokes County",
        },
        "27027": {"Rockingham County": "Rockingham County"},
        "27028": {"Davie County": "Davie County", "Iredell County": "Iredell County"},
        "27030": {"Surry County": "Surry County", "Stokes County": "Stokes County"},
        "27040": {"Forsyth County": "Forsyth County"},
        "27041": {"Surry County": "Surry County", "Stokes County": "Stokes County"},
        "27042": {"Stokes County": "Stokes County"},
        "27043": {
            "Stokes County": "Stokes County",
            "Surry County": "Surry County",
            "Forsyth County": "Forsyth County",
        },
        "27045": {"Forsyth County": "Forsyth County", "Stokes County": "Stokes County"},
        "27046": {"Stokes County": "Stokes County"},
        "27047": {"Surry County": "Surry County"},
        "27048": {"Rockingham County": "Rockingham County"},
        "27049": {"Surry County": "Surry County"},
        "27050": {"Forsyth County": "Forsyth County", "Stokes County": "Stokes County"},
        "27051": {"Forsyth County": "Forsyth County"},
        "27052": {"Stokes County": "Stokes County", "Forsyth County": "Forsyth County"},
        "27053": {"Stokes County": "Stokes County", "Surry County": "Surry County"},
        "27054": {"Rowan County": "Rowan County"},
        "27055": {
            "Yadkin County": "Yadkin County",
            "Davie County": "Davie County",
            "Iredell County": "Iredell County",
        },
        "27094": {"Forsyth County": "Forsyth County"},
        "27099": {"Forsyth County": "Forsyth County"},
        "27101": {"Forsyth County": "Forsyth County"},
        "27102": {"Forsyth County": "Forsyth County"},
        "27103": {"Forsyth County": "Forsyth County"},
        "27104": {"Forsyth County": "Forsyth County"},
        "27105": {"Forsyth County": "Forsyth County"},
        "27106": {"Forsyth County": "Forsyth County"},
        "27107": {
            "Davidson County": "Davidson County",
            "Forsyth County": "Forsyth County",
        },
        "27108": {"Forsyth County": "Forsyth County"},
        "27109": {"Forsyth County": "Forsyth County"},
        "27110": {"Forsyth County": "Forsyth County"},
        "27111": {"Forsyth County": "Forsyth County"},
        "27113": {"Forsyth County": "Forsyth County"},
        "27114": {"Forsyth County": "Forsyth County"},
        "27115": {"Forsyth County": "Forsyth County"},
        "27116": {"Forsyth County": "Forsyth County"},
        "27117": {"Forsyth County": "Forsyth County"},
        "27120": {"Forsyth County": "Forsyth County"},
        "27127": {
            "Forsyth County": "Forsyth County",
            "Davidson County": "Davidson County",
        },
        "27130": {"Forsyth County": "Forsyth County"},
        "27150": {"Forsyth County": "Forsyth County"},
        "27152": {"Forsyth County": "Forsyth County"},
        "27155": {"Forsyth County": "Forsyth County"},
        "27157": {"Forsyth County": "Forsyth County"},
        "27199": {"Forsyth County": "Forsyth County"},
        "27201": {"Alamance County": "Alamance County"},
        "27202": {"Alamance County": "Alamance County"},
        "27203": {"Randolph County": "Randolph County"},
        "27205": {"Randolph County": "Randolph County"},
        "27207": {"Chatham County": "Chatham County"},
        "27208": {
            "Chatham County": "Chatham County",
            "Randolph County": "Randolph County",
            "Moore County": "Moore County",
        },
        "27209": {
            "Montgomery County": "Montgomery County",
            "Moore County": "Moore County",
        },
        "27212": {"Caswell County": "Caswell County"},
        "27213": {"Chatham County": "Chatham County"},
        "27214": {
            "Guilford County": "Guilford County",
            "Rockingham County": "Rockingham County",
        },
        "27215": {
            "Alamance County": "Alamance County",
            "Guilford County": "Guilford County",
        },
        "27216": {"Alamance County": "Alamance County"},
        "27217": {
            "Alamance County": "Alamance County",
            "Caswell County": "Caswell County",
        },
        "27229": {
            "Montgomery County": "Montgomery County",
            "Richmond County": "Richmond County",
        },
        "27230": {"Randolph County": "Randolph County"},
        "27231": {
            "Orange County": "Orange County",
            "Caswell County": "Caswell County",
            "Person County": "Person County",
        },
        "27233": {
            "Randolph County": "Randolph County",
            "Guilford County": "Guilford County",
        },
        "27235": {"Guilford County": "Guilford County"},
        "27239": {
            "Davidson County": "Davidson County",
            "Randolph County": "Randolph County",
        },
        "27242": {"Moore County": "Moore County"},
        "27243": {"Orange County": "Orange County"},
        "27244": {
            "Alamance County": "Alamance County",
            "Caswell County": "Caswell County",
            "Guilford County": "Guilford County",
        },
        "27247": {"Montgomery County": "Montgomery County"},
        "27248": {"Randolph County": "Randolph County"},
        "27249": {
            "Guilford County": "Guilford County",
            "Alamance County": "Alamance County",
            "Rockingham County": "Rockingham County",
            "Caswell County": "Caswell County",
        },
        "27252": {"Chatham County": "Chatham County"},
        "27253": {"Alamance County": "Alamance County"},
        "27256": {"Chatham County": "Chatham County"},
        "27258": {"Alamance County": "Alamance County"},
        "27259": {"Moore County": "Moore County"},
        "27260": {
            "Guilford County": "Guilford County",
            "Randolph County": "Randolph County",
        },
        "27261": {"Guilford County": "Guilford County"},
        "27262": {
            "Guilford County": "Guilford County",
            "Davidson County": "Davidson County",
            "Randolph County": "Randolph County",
        },
        "27263": {
            "Randolph County": "Randolph County",
            "Guilford County": "Guilford County",
        },
        "27264": {"Guilford County": "Guilford County"},
        "27265": {
            "Guilford County": "Guilford County",
            "Davidson County": "Davidson County",
            "Forsyth County": "Forsyth County",
        },
        "27268": {"Guilford County": "Guilford County"},
        "27278": {"Orange County": "Orange County", "Durham County": "Durham County"},
        "27281": {
            "Moore County": "Moore County",
            "Montgomery County": "Montgomery County",
            "Richmond County": "Richmond County",
        },
        "27282": {"Guilford County": "Guilford County"},
        "27283": {
            "Guilford County": "Guilford County",
            "Randolph County": "Randolph County",
        },
        "27284": {
            "Forsyth County": "Forsyth County",
            "Guilford County": "Guilford County",
            "Davidson County": "Davidson County",
        },
        "27285": {"Forsyth County": "Forsyth County"},
        "27288": {"Rockingham County": "Rockingham County"},
        "27289": {"Rockingham County": "Rockingham County"},
        "27291": {"Caswell County": "Caswell County", "Person County": "Person County"},
        "27292": {
            "Davidson County": "Davidson County",
            "Randolph County": "Randolph County",
        },
        "27293": {"Davidson County": "Davidson County"},
        "27294": {"Davidson County": "Davidson County"},
        "27295": {"Davidson County": "Davidson County"},
        "27298": {
            "Randolph County": "Randolph County",
            "Alamance County": "Alamance County",
            "Guilford County": "Guilford County",
            "Chatham County": "Chatham County",
        },
        "27299": {"Davidson County": "Davidson County"},
        "27301": {"Guilford County": "Guilford County"},
        "27302": {
            "Alamance County": "Alamance County",
            "Orange County": "Orange County",
            "Caswell County": "Caswell County",
        },
        "27305": {"Caswell County": "Caswell County", "Person County": "Person County"},
        "27306": {
            "Montgomery County": "Montgomery County",
            "Richmond County": "Richmond County",
        },
        "27310": {"Guilford County": "Guilford County"},
        "27311": {
            "Caswell County": "Caswell County",
            "Rockingham County": "Rockingham County",
        },
        "27312": {
            "Chatham County": "Chatham County",
            "Alamance County": "Alamance County",
        },
        "27313": {
            "Guilford County": "Guilford County",
            "Randolph County": "Randolph County",
        },
        "27314": {"Caswell County": "Caswell County"},
        "27315": {"Caswell County": "Caswell County"},
        "27316": {"Randolph County": "Randolph County"},
        "27317": {
            "Randolph County": "Randolph County",
            "Guilford County": "Guilford County",
        },
        "27320": {
            "Rockingham County": "Rockingham County",
            "Caswell County": "Caswell County",
            "Guilford County": "Guilford County",
        },
        "27325": {"Moore County": "Moore County", "Randolph County": "Randolph County"},
        "27326": {
            "Rockingham County": "Rockingham County",
            "Caswell County": "Caswell County",
        },
        "27330": {
            "Lee County": "Lee County",
            "Chatham County": "Chatham County",
            "Moore County": "Moore County",
            "Harnett County": "Harnett County",
        },
        "27331": {"Lee County": "Lee County"},
        "27332": {"Lee County": "Lee County", "Harnett County": "Harnett County"},
        "27340": {"Alamance County": "Alamance County"},
        "27341": {
            "Randolph County": "Randolph County",
            "Moore County": "Moore County",
            "Montgomery County": "Montgomery County",
        },
        "27342": {"Guilford County": "Guilford County"},
        "27343": {"Person County": "Person County", "Caswell County": "Caswell County"},
        "27344": {
            "Chatham County": "Chatham County",
            "Randolph County": "Randolph County",
        },
        "27349": {
            "Alamance County": "Alamance County",
            "Chatham County": "Chatham County",
        },
        "27350": {"Randolph County": "Randolph County"},
        "27351": {"Davidson County": "Davidson County"},
        "27355": {
            "Randolph County": "Randolph County",
            "Chatham County": "Chatham County",
        },
        "27356": {
            "Montgomery County": "Montgomery County",
            "Moore County": "Moore County",
        },
        "27357": {
            "Rockingham County": "Rockingham County",
            "Guilford County": "Guilford County",
            "Stokes County": "Stokes County",
        },
        "27358": {
            "Guilford County": "Guilford County",
            "Rockingham County": "Rockingham County",
        },
        "27359": {"Alamance County": "Alamance County"},
        "27360": {
            "Davidson County": "Davidson County",
            "Randolph County": "Randolph County",
        },
        "27370": {"Randolph County": "Randolph County"},
        "27371": {
            "Montgomery County": "Montgomery County",
            "Randolph County": "Randolph County",
        },
        "27373": {"Davidson County": "Davidson County"},
        "27374": {"Davidson County": "Davidson County"},
        "27375": {"Rockingham County": "Rockingham County"},
        "27376": {"Moore County": "Moore County"},
        "27377": {"Guilford County": "Guilford County"},
        "27379": {"Caswell County": "Caswell County"},
        "27401": {"Guilford County": "Guilford County"},
        "27402": {"Guilford County": "Guilford County"},
        "27403": {"Guilford County": "Guilford County"},
        "27404": {"Guilford County": "Guilford County"},
        "27405": {"Guilford County": "Guilford County"},
        "27406": {"Guilford County": "Guilford County"},
        "27407": {"Guilford County": "Guilford County"},
        "27408": {"Guilford County": "Guilford County"},
        "27409": {"Guilford County": "Guilford County"},
        "27410": {"Guilford County": "Guilford County"},
        "27411": {"Guilford County": "Guilford County"},
        "27412": {"Guilford County": "Guilford County"},
        "27413": {"Guilford County": "Guilford County"},
        "27415": {"Guilford County": "Guilford County"},
        "27416": {"Guilford County": "Guilford County"},
        "27417": {"Guilford County": "Guilford County"},
        "27419": {"Guilford County": "Guilford County"},
        "27420": {"Guilford County": "Guilford County"},
        "27425": {"Guilford County": "Guilford County"},
        "27429": {"Guilford County": "Guilford County"},
        "27435": {"Guilford County": "Guilford County"},
        "27438": {"Guilford County": "Guilford County"},
        "27455": {"Guilford County": "Guilford County"},
        "27495": {"Guilford County": "Guilford County"},
        "27497": {"Guilford County": "Guilford County"},
        "27498": {"Guilford County": "Guilford County"},
        "27499": {"Guilford County": "Guilford County"},
        "27501": {
            "Harnett County": "Harnett County",
            "Johnston County": "Johnston County",
            "Wake County": "Wake County",
        },
        "27502": {"Wake County": "Wake County", "Chatham County": "Chatham County"},
        "27503": {"Durham County": "Durham County"},
        "27504": {
            "Johnston County": "Johnston County",
            "Harnett County": "Harnett County",
        },
        "27505": {"Harnett County": "Harnett County", "Lee County": "Lee County"},
        "27506": {"Harnett County": "Harnett County"},
        "27507": {
            "Granville County": "Granville County",
            "Vance County": "Vance County",
        },
        "27508": {"Franklin County": "Franklin County"},
        "27509": {"Granville County": "Granville County"},
        "27510": {"Orange County": "Orange County"},
        "27511": {"Wake County": "Wake County"},
        "27512": {"Wake County": "Wake County"},
        "27513": {"Wake County": "Wake County"},
        "27514": {"Orange County": "Orange County"},
        "27515": {"Orange County": "Orange County"},
        "27516": {"Orange County": "Orange County", "Chatham County": "Chatham County"},
        "27517": {
            "Chatham County": "Chatham County",
            "Orange County": "Orange County",
            "Durham County": "Durham County",
        },
        "27518": {"Wake County": "Wake County"},
        "27519": {"Wake County": "Wake County", "Chatham County": "Chatham County"},
        "27520": {"Johnston County": "Johnston County", "Wake County": "Wake County"},
        "27521": {"Harnett County": "Harnett County"},
        "27522": {"Granville County": "Granville County", "Wake County": "Wake County"},
        "27523": {"Chatham County": "Chatham County", "Wake County": "Wake County"},
        "27524": {"Johnston County": "Johnston County", "Wayne County": "Wayne County"},
        "27525": {
            "Franklin County": "Franklin County",
            "Granville County": "Granville County",
        },
        "27526": {"Harnett County": "Harnett County", "Wake County": "Wake County"},
        "27527": {"Johnston County": "Johnston County"},
        "27528": {"Johnston County": "Johnston County"},
        "27529": {"Wake County": "Wake County", "Johnston County": "Johnston County"},
        "27530": {"Wayne County": "Wayne County"},
        "27531": {"Wayne County": "Wayne County"},
        "27532": {"Wayne County": "Wayne County"},
        "27533": {"Wayne County": "Wayne County"},
        "27534": {"Wayne County": "Wayne County", "Greene County": "Greene County"},
        "27536": {"Vance County": "Vance County"},
        "27537": {
            "Vance County": "Vance County",
            "Franklin County": "Franklin County",
            "Warren County": "Warren County",
        },
        "27539": {"Wake County": "Wake County"},
        "27540": {
            "Wake County": "Wake County",
            "Harnett County": "Harnett County",
            "Chatham County": "Chatham County",
        },
        "27541": {
            "Person County": "Person County",
            "Orange County": "Orange County",
            "Caswell County": "Caswell County",
        },
        "27542": {
            "Johnston County": "Johnston County",
            "Wilson County": "Wilson County",
            "Wayne County": "Wayne County",
        },
        "27543": {"Harnett County": "Harnett County"},
        "27544": {
            "Vance County": "Vance County",
            "Franklin County": "Franklin County",
            "Granville County": "Granville County",
        },
        "27545": {"Wake County": "Wake County"},
        "27546": {"Harnett County": "Harnett County"},
        "27549": {"Franklin County": "Franklin County"},
        "27551": {"Warren County": "Warren County"},
        "27552": {"Harnett County": "Harnett County"},
        "27553": {"Warren County": "Warren County", "Vance County": "Vance County"},
        "27555": {"Johnston County": "Johnston County"},
        "27556": {"Vance County": "Vance County"},
        "27557": {
            "Nash County": "Nash County",
            "Johnston County": "Johnston County",
            "Wilson County": "Wilson County",
            "Franklin County": "Franklin County",
        },
        "27559": {"Chatham County": "Chatham County"},
        "27560": {"Wake County": "Wake County", "Durham County": "Durham County"},
        "27562": {"Chatham County": "Chatham County", "Wake County": "Wake County"},
        "27563": {"Warren County": "Warren County", "Vance County": "Vance County"},
        "27565": {
            "Granville County": "Granville County",
            "Vance County": "Vance County",
            "Person County": "Person County",
        },
        "27568": {"Johnston County": "Johnston County"},
        "27569": {"Johnston County": "Johnston County", "Wayne County": "Wayne County"},
        "27570": {"Warren County": "Warren County"},
        "27571": {"Wake County": "Wake County"},
        "27572": {
            "Person County": "Person County",
            "Durham County": "Durham County",
            "Orange County": "Orange County",
            "Granville County": "Granville County",
        },
        "27573": {"Person County": "Person County"},
        "27574": {
            "Person County": "Person County",
            "Granville County": "Granville County",
        },
        "27576": {"Johnston County": "Johnston County"},
        "27577": {"Johnston County": "Johnston County"},
        "27581": {"Granville County": "Granville County"},
        "27582": {"Granville County": "Granville County"},
        "27583": {
            "Person County": "Person County",
            "Orange County": "Orange County",
            "Durham County": "Durham County",
        },
        "27584": {"Vance County": "Vance County"},
        "27586": {"Warren County": "Warren County"},
        "27587": {
            "Wake County": "Wake County",
            "Granville County": "Granville County",
            "Franklin County": "Franklin County",
        },
        "27588": {"Wake County": "Wake County"},
        "27589": {
            "Warren County": "Warren County",
            "Franklin County": "Franklin County",
        },
        "27591": {"Wake County": "Wake County", "Johnston County": "Johnston County"},
        "27592": {
            "Wake County": "Wake County",
            "Johnston County": "Johnston County",
            "Harnett County": "Harnett County",
        },
        "27593": {"Johnston County": "Johnston County"},
        "27594": {"Warren County": "Warren County"},
        "27596": {
            "Franklin County": "Franklin County",
            "Wake County": "Wake County",
            "Granville County": "Granville County",
        },
        "27597": {
            "Wake County": "Wake County",
            "Franklin County": "Franklin County",
            "Johnston County": "Johnston County",
            "Nash County": "Nash County",
        },
        "27599": {"Orange County": "Orange County"},
        "27601": {"Wake County": "Wake County"},
        "27602": {"Wake County": "Wake County"},
        "27603": {"Wake County": "Wake County", "Johnston County": "Johnston County"},
        "27604": {"Wake County": "Wake County"},
        "27605": {"Wake County": "Wake County"},
        "27606": {"Wake County": "Wake County"},
        "27607": {"Wake County": "Wake County"},
        "27608": {"Wake County": "Wake County"},
        "27609": {"Wake County": "Wake County"},
        "27610": {"Wake County": "Wake County", "Johnston County": "Johnston County"},
        "27611": {"Wake County": "Wake County"},
        "27612": {"Wake County": "Wake County"},
        "27613": {"Wake County": "Wake County", "Durham County": "Durham County"},
        "27614": {"Wake County": "Wake County"},
        "27615": {"Wake County": "Wake County"},
        "27616": {"Wake County": "Wake County"},
        "27617": {"Wake County": "Wake County", "Durham County": "Durham County"},
        "27619": {"Wake County": "Wake County"},
        "27620": {"Wake County": "Wake County"},
        "27622": {"Wake County": "Wake County"},
        "27623": {"Wake County": "Wake County"},
        "27624": {"Wake County": "Wake County"},
        "27627": {"Wake County": "Wake County"},
        "27628": {"Wake County": "Wake County"},
        "27629": {"Wake County": "Wake County"},
        "27636": {"Wake County": "Wake County"},
        "27640": {"Wake County": "Wake County"},
        "27656": {"Wake County": "Wake County"},
        "27658": {"Wake County": "Wake County"},
        "27661": {"Wake County": "Wake County"},
        "27675": {"Wake County": "Wake County"},
        "27676": {"Wake County": "Wake County"},
        "27690": {"Wake County": "Wake County"},
        "27695": {"Wake County": "Wake County"},
        "27697": {"Wake County": "Wake County"},
        "27699": {"Wake County": "Wake County"},
        "27701": {"Durham County": "Durham County"},
        "27702": {"Durham County": "Durham County"},
        "27703": {"Durham County": "Durham County", "Wake County": "Wake County"},
        "27704": {"Durham County": "Durham County"},
        "27705": {"Durham County": "Durham County", "Orange County": "Orange County"},
        "27706": {"Durham County": "Durham County"},
        "27707": {"Durham County": "Durham County", "Orange County": "Orange County"},
        "27708": {"Durham County": "Durham County"},
        "27709": {"Durham County": "Durham County"},
        "27710": {"Durham County": "Durham County"},
        "27712": {"Durham County": "Durham County", "Orange County": "Orange County"},
        "27713": {
            "Durham County": "Durham County",
            "Chatham County": "Chatham County",
            "Wake County": "Wake County",
        },
        "27715": {"Durham County": "Durham County"},
        "27717": {"Durham County": "Durham County"},
        "27722": {"Durham County": "Durham County"},
        "27801": {"Edgecombe County": "Edgecombe County"},
        "27802": {"Edgecombe County": "Edgecombe County"},
        "27803": {
            "Nash County": "Nash County",
            "Wilson County": "Wilson County",
            "Edgecombe County": "Edgecombe County",
        },
        "27804": {"Nash County": "Nash County"},
        "27805": {
            "Bertie County": "Bertie County",
            "Hertford County": "Hertford County",
        },
        "27806": {"Beaufort County": "Beaufort County"},
        "27807": {"Nash County": "Nash County", "Wilson County": "Wilson County"},
        "27808": {"Beaufort County": "Beaufort County"},
        "27809": {"Edgecombe County": "Edgecombe County", "Nash County": "Nash County"},
        "27810": {"Hyde County": "Hyde County", "Beaufort County": "Beaufort County"},
        "27811": {"Pitt County": "Pitt County"},
        "27812": {
            "Pitt County": "Pitt County",
            "Edgecombe County": "Edgecombe County",
            "Martin County": "Martin County",
        },
        "27813": {"Wilson County": "Wilson County"},
        "27814": {"Beaufort County": "Beaufort County"},
        "27815": {"Edgecombe County": "Edgecombe County"},
        "27816": {"Franklin County": "Franklin County", "Nash County": "Nash County"},
        "27817": {"Beaufort County": "Beaufort County"},
        "27818": {"Hertford County": "Hertford County"},
        "27819": {"Edgecombe County": "Edgecombe County"},
        "27820": {"Northampton County": "Northampton County"},
        "27821": {"Beaufort County": "Beaufort County"},
        "27822": {
            "Wilson County": "Wilson County",
            "Nash County": "Nash County",
            "Edgecombe County": "Edgecombe County",
        },
        "27823": {"Halifax County": "Halifax County"},
        "27824": {"Hyde County": "Hyde County"},
        "27825": {"Martin County": "Martin County"},
        "27826": {"Hyde County": "Hyde County", "Tyrrell County": "Tyrrell County"},
        "27827": {"Pitt County": "Pitt County"},
        "27828": {"Pitt County": "Pitt County", "Greene County": "Greene County"},
        "27829": {
            "Pitt County": "Pitt County",
            "Edgecombe County": "Edgecombe County",
            "Wilson County": "Wilson County",
        },
        "27830": {"Wayne County": "Wayne County", "Wilson County": "Wilson County"},
        "27831": {"Northampton County": "Northampton County"},
        "27832": {"Northampton County": "Northampton County"},
        "27833": {"Pitt County": "Pitt County"},
        "27834": {
            "Pitt County": "Pitt County",
            "Beaufort County": "Beaufort County",
            "Edgecombe County": "Edgecombe County",
        },
        "27835": {"Pitt County": "Pitt County"},
        "27836": {"Pitt County": "Pitt County"},
        "27837": {"Pitt County": "Pitt County", "Beaufort County": "Beaufort County"},
        "27839": {"Halifax County": "Halifax County"},
        "27840": {"Martin County": "Martin County"},
        "27841": {"Martin County": "Martin County"},
        "27842": {
            "Northampton County": "Northampton County",
            "Warren County": "Warren County",
        },
        "27843": {
            "Edgecombe County": "Edgecombe County",
            "Martin County": "Martin County",
            "Halifax County": "Halifax County",
        },
        "27844": {
            "Halifax County": "Halifax County",
            "Warren County": "Warren County",
            "Nash County": "Nash County",
            "Franklin County": "Franklin County",
        },
        "27845": {"Northampton County": "Northampton County"},
        "27846": {"Martin County": "Martin County"},
        "27847": {"Bertie County": "Bertie County"},
        "27849": {"Bertie County": "Bertie County"},
        "27850": {"Halifax County": "Halifax County", "Warren County": "Warren County"},
        "27851": {"Wilson County": "Wilson County", "Wayne County": "Wayne County"},
        "27852": {
            "Edgecombe County": "Edgecombe County",
            "Pitt County": "Pitt County",
            "Wilson County": "Wilson County",
        },
        "27853": {"Northampton County": "Northampton County"},
        "27855": {
            "Hertford County": "Hertford County",
            "Northampton County": "Northampton County",
        },
        "27856": {"Nash County": "Nash County"},
        "27857": {"Martin County": "Martin County"},
        "27858": {"Pitt County": "Pitt County"},
        "27860": {
            "Beaufort County": "Beaufort County",
            "Washington County": "Washington County",
            "Hyde County": "Hyde County",
        },
        "27861": {"Martin County": "Martin County"},
        "27862": {"Northampton County": "Northampton County"},
        "27863": {
            "Wayne County": "Wayne County",
            "Greene County": "Greene County",
            "Johnston County": "Johnston County",
        },
        "27864": {"Edgecombe County": "Edgecombe County"},
        "27865": {"Beaufort County": "Beaufort County"},
        "27866": {"Northampton County": "Northampton County"},
        "27867": {"Northampton County": "Northampton County"},
        "27868": {"Nash County": "Nash County"},
        "27869": {
            "Northampton County": "Northampton County",
            "Bertie County": "Bertie County",
        },
        "27870": {"Halifax County": "Halifax County"},
        "27871": {
            "Martin County": "Martin County",
            "Pitt County": "Pitt County",
            "Beaufort County": "Beaufort County",
        },
        "27872": {"Bertie County": "Bertie County"},
        "27873": {"Wilson County": "Wilson County"},
        "27874": {"Halifax County": "Halifax County"},
        "27875": {"Hyde County": "Hyde County"},
        "27876": {"Northampton County": "Northampton County"},
        "27877": {"Northampton County": "Northampton County"},
        "27878": {
            "Nash County": "Nash County",
            "Wilson County": "Wilson County",
            "Edgecombe County": "Edgecombe County",
        },
        "27879": {"Pitt County": "Pitt County"},
        "27880": {"Wilson County": "Wilson County", "Nash County": "Nash County"},
        "27881": {"Edgecombe County": "Edgecombe County"},
        "27882": {"Nash County": "Nash County", "Franklin County": "Franklin County"},
        "27883": {
            "Wilson County": "Wilson County",
            "Greene County": "Greene County",
            "Wayne County": "Wayne County",
        },
        "27884": {"Pitt County": "Pitt County"},
        "27885": {"Hyde County": "Hyde County"},
        "27886": {"Edgecombe County": "Edgecombe County", "Pitt County": "Pitt County"},
        "27887": {"Halifax County": "Halifax County"},
        "27888": {
            "Greene County": "Greene County",
            "Wilson County": "Wilson County",
            "Pitt County": "Pitt County",
        },
        "27889": {
            "Beaufort County": "Beaufort County",
            "Pitt County": "Pitt County",
            "Martin County": "Martin County",
        },
        "27890": {"Halifax County": "Halifax County"},
        "27891": {
            "Nash County": "Nash County",
            "Edgecombe County": "Edgecombe County",
            "Halifax County": "Halifax County",
        },
        "27892": {
            "Martin County": "Martin County",
            "Beaufort County": "Beaufort County",
        },
        "27893": {"Wilson County": "Wilson County"},
        "27894": {"Wilson County": "Wilson County"},
        "27895": {"Wilson County": "Wilson County"},
        "27896": {"Wilson County": "Wilson County", "Nash County": "Nash County"},
        "27897": {
            "Northampton County": "Northampton County",
            "Hertford County": "Hertford County",
        },
        "27906": {"Pasquotank County": "Pasquotank County"},
        "27907": {"Pasquotank County": "Pasquotank County"},
        "27909": {"Pasquotank County": "Pasquotank County"},
        "27910": {
            "Hertford County": "Hertford County",
            "Bertie County": "Bertie County",
        },
        "27915": {"Dare County": "Dare County"},
        "27916": {"Currituck County": "Currituck County"},
        "27917": {"Currituck County": "Currituck County"},
        "27919": {
            "Perquimans County": "Perquimans County",
            "Chowan County": "Chowan County",
        },
        "27920": {"Dare County": "Dare County"},
        "27921": {"Camden County": "Camden County"},
        "27922": {"Hertford County": "Hertford County"},
        "27923": {"Currituck County": "Currituck County"},
        "27924": {
            "Bertie County": "Bertie County",
            "Hertford County": "Hertford County",
        },
        "27925": {"Tyrrell County": "Tyrrell County"},
        "27926": {"Gates County": "Gates County"},
        "27927": {"Currituck County": "Currituck County"},
        "27928": {
            "Washington County": "Washington County",
            "Tyrrell County": "Tyrrell County",
        },
        "27929": {"Currituck County": "Currituck County"},
        "27932": {
            "Chowan County": "Chowan County",
            "Perquimans County": "Perquimans County",
        },
        "27935": {"Gates County": "Gates County"},
        "27936": {"Dare County": "Dare County"},
        "27937": {"Gates County": "Gates County"},
        "27938": {"Gates County": "Gates County"},
        "27939": {"Currituck County": "Currituck County"},
        "27941": {"Currituck County": "Currituck County"},
        "27942": {"Hertford County": "Hertford County"},
        "27943": {"Dare County": "Dare County"},
        "27944": {"Perquimans County": "Perquimans County"},
        "27946": {"Gates County": "Gates County", "Chowan County": "Chowan County"},
        "27947": {"Currituck County": "Currituck County"},
        "27948": {"Dare County": "Dare County"},
        "27949": {"Dare County": "Dare County"},
        "27950": {"Currituck County": "Currituck County"},
        "27953": {"Dare County": "Dare County"},
        "27954": {"Dare County": "Dare County"},
        "27956": {"Currituck County": "Currituck County"},
        "27957": {"Bertie County": "Bertie County"},
        "27958": {"Currituck County": "Currituck County"},
        "27959": {"Dare County": "Dare County"},
        "27960": {"Hyde County": "Hyde County"},
        "27962": {
            "Washington County": "Washington County",
            "Beaufort County": "Beaufort County",
        },
        "27964": {"Currituck County": "Currituck County"},
        "27965": {"Currituck County": "Currituck County"},
        "27966": {"Currituck County": "Currituck County"},
        "27967": {"Bertie County": "Bertie County"},
        "27968": {"Dare County": "Dare County"},
        "27969": {"Gates County": "Gates County"},
        "27970": {"Washington County": "Washington County"},
        "27972": {"Dare County": "Dare County"},
        "27973": {
            "Currituck County": "Currituck County",
            "Camden County": "Camden County",
        },
        "27974": {"Camden County": "Camden County"},
        "27976": {"Camden County": "Camden County"},
        "27978": {"Dare County": "Dare County"},
        "27979": {"Gates County": "Gates County"},
        "27980": {
            "Chowan County": "Chowan County",
            "Perquimans County": "Perquimans County",
        },
        "27981": {"Dare County": "Dare County"},
        "27982": {"Dare County": "Dare County"},
        "27983": {"Bertie County": "Bertie County"},
        "27985": {"Perquimans County": "Perquimans County"},
        "27986": {"Hertford County": "Hertford County"},
        "28001": {"Stanly County": "Stanly County"},
        "28002": {"Stanly County": "Stanly County"},
        "28006": {"Gaston County": "Gaston County"},
    }

    category_benefits = {
        "cash": {
            "benefits": {
                "tanf": {
                    "name": {
                        "_label": "cashAssistanceBenefits.tanf",
                        "_default_message": "Work First Family Assistance (Temporary Assistance for Needy Families (TANF)):  ",
                    },
                    "description": {
                        "_label": "cashAssistanceBenefits.tanf_desc",
                        "_default_message": "Cash assistance and work support",
                    },
                },
                "ssi": {
                    "name": {
                        "_label": "cashAssistanceBenefits.ssi",
                        "_default_message": "Supplemental Security Income (SSI): ",
                    },
                    "description": {
                        "_label": "cashAssistanceBenefits.ssi_desc",
                        "_default_message": "Federal cash assistance for individuals who are disabled, blind, or 65 years of age or older",
                    },
                },
                "ssdi": {
                    "name": {
                        "_label": "cashAssistanceBenefits.ssdi",
                        "_default_message": "Social Security Disability Insurance (SSDI): ",
                    },
                    "description": {
                        "_label": "cashAssistanceBenefits.ssdi_desc",
                        "_default_message": "Social security benefit for people with disabilities",
                    },
                },
            },
            "category_name": {
                "_label": "cashAssistance",
                "_default_message": "Cash Assistance",
            },
        },
        "foodAndNutrition": {
            "benefits": {
                "snap": {
                    "name": {
                        "_label": "foodAndNutritionBenefits.snap",
                        "_default_message": "Supplemental Nutrition Assistance Program (SNAP): ",
                    },
                    "description": {
                        "_label": "foodAndNutritionBenefits.snap_desc",
                        "_default_message": "Food assistance",
                    },
                },
                "wic": {
                    "name": {
                        "_label": "foodAndNutritionBenefits.wic",
                        "_default_message": "Special Supplemental Nutrition Program for Women, Infants, and Children (WIC): ",
                    },
                    "description": {
                        "_label": "foodAndNutritionBenefits.wic_desc",
                        "_default_message": "Food and breastfeeding assistance",
                    },
                },
                "nslp": {
                    "name": {
                        "_label": "foodAndNutritionBenefits.nslp",
                        "_default_message": "National School Lunch Program: ",
                    },
                    "description": {
                        "_label": "foodAndNutritionBenefits.nslp_desc",
                        "_default_message": "Free school meals",
                    },
                },
            },
            "category_name": {
                "_label": "foodAndNutrition",
                "_default_message": "Food and Nutrition",
            },
        },
        "childCare": {
            "benefits": {
                "cccap": {
                    "name": {
                        "_label": "childCareBenefits.cccap",
                        "_default_message": "NC Child Care Subsidy (CCCAP): ",
                    },
                    "description": {
                        "_label": "childCareBenefits.cccap_desc",
                        "_default_message": "Help with child care costs",
                    },
                },
                "coheadstart": {
                    "name": {
                        "_label": "childCareBenefits.coheadstart",
                        "_default_message": "NC Pre-K Program: ",
                    },
                    "description": {
                        "_label": "childCareBenefits.coheadstart_desc",
                        "_default_message": "Free early child care and preschool",
                    },
                },
                "pell": {
                    "name": {
                        "_label": "childCareBenefits.pell",
                        "_default_message": "Pell Grant: ",
                    },
                    "description": {
                        "_label": "childCareBenefits.pell_desc",
                        "_default_message": "Federal grant to help with the cost of college or technical school",
                    },
                },
            },
            "category_name": {
                "_label": "childCareYouthAndEducation",
                "_default_message": "Child Care, Youth, and Education",
            },
        },
        "housingAndUtilities": {
            "benefits": {
                "acp": {
                    "name": {
                        "_label": "housingAndUtilities.acp",
                        "_default_message": "Affordable Connectivity Program (ACP): ",
                    },
                    "description": {
                        "_label": "housingAndUtilities.acp_desc",
                        "_default_message": "Home internet discount",
                    },
                },
                "lifeline": {
                    "name": {
                        "_label": "housingAndUtilities.lifeline",
                        "_default_message": "Lifeline: ",
                    },
                    "description": {
                        "_label": "housingAndUtilities.lifeline_desc",
                        "_default_message": "Phone or internet discount",
                    },
                },
                "leap": {
                    "name": {
                        "_label": "housingAndUtilities.leap",
                        "_default_message": "Low-Income Energy Assistance Program (LEAP): ",
                    },
                    "description": {
                        "_label": "housingAndUtilities.leap_desc",
                        "_default_message": "Help with winter heating bills",
                    },
                },
                "cowap": {
                    "name": {
                        "_label": "housingAndUtilities.cowap",
                        "_default_message": "Weatherization Assistance Program: ",
                    },
                    "description": {
                        "_label": "housingAndUtilities.cowap_desc",
                        "_default_message": "Free home energy upgrades",
                    },
                },
            },
            "category_name": {
                "_label": "housingAndUtilities",
                "_default_message": "Housing and Utilities",
            },
        },
        "taxCredits": {
            "benefits": {
                "eitc": {
                    "name": {
                        "_label": "taxCreditBenefits.eitc",
                        "_default_message": "Earned Income Tax Credit (EITC): ",
                    },
                    "description": {
                        "_label": "taxCreditBenefits.eitc_desc",
                        "_default_message": "Federal tax credit - earned income",
                    },
                },
                "ctc": {
                    "name": {
                        "_label": "taxCreditBenefits.ctc",
                        "_default_message": "Child Tax Credit (CTC): ",
                    },
                    "description": {
                        "_label": "taxCreditBenefits.ctc_desc",
                        "_default_message": "Federal tax credit",
                    },
                },
            },
            "category_name": {
                "_label": "taxCredits",
                "_default_message": "Tax Credits",
            },
        },
    }

    consent_to_contact = {
        "en-us": "https://bennc.org/additional-terms-and-consent-to-contact/",
        "es": "https://nc.myfriendben.org/es/additional-terms-and-consent-to-contact",
        "fr": "https://nc.myfriendben.org/fr/additional-terms-and-consent-to-contact",
        "vi": "https://nc.myfriendben.org/vi/additional-terms-and-consent-to-contact",
    }

    privacy_policy = {
        "en-us": "https://bennc.org/privacy-policy/",
        "es": "https://nc.myfriendben.org/es/data-privacy-policy",
        "fr": "https://nc.myfriendben.org/fr/data-privacy-policy",
        "vi": "https://nc.myfriendben.org/vi/data-privacy-policy",
    }

    referrer_data = {
        "theme": {"default": "default", "211co": "twoOneOne"},
        "logoSource": {
            "default": "MFB_NCLogo",
            "bia": "BIA_MFBLogo",
            "jeffcoHS": "JHSA_MFBLogo",
            "jeffcoHSCM": "JHSA_MFBLogo",
            "villageExchange": "VE_Logo",
            "cch": "CCH_MFBLogo",
            "lgs": "LGS_Logo",
            "gac": "GAC_Logo",
            "fircsummitresourcecenter": "FIRC_Logo",
            "coBenefits": "CO_MFBLogo",
            "dhs": "DHS_MFBLogo",
        },
        "logoAlt": {
            "default": {
                "id": "referrerHook.logoAlts.default",
                "defaultMessage": "MyFriendBen home page button",
            },
            "bia": {
                "id": "referrerHook.logoAlts.bia",
                "defaultMessage": "Benefits in Action and MyFriendBen home page button",
            },
            "jeffcoHS": {
                "id": "referrerHook.logoAlts.jeffcoHS",
                "defaultMessage": "Jeffco Human Services and MyFriendBen home page button",
            },
            "jeffcoHSCM": {
                "id": "referrerHook.logoAlts.jeffcoHSCM",
                "defaultMessage": "Jeffco Human Services and MyFriendBen home page button",
            },
            "cch": {
                "id": "referrerHook.logoAlts.cch",
                "defaultMessage": "Colorado Coalition for the Homeless and MyFriendBen home page button",
            },
            "lgs": {
                "id": "referrerHook.logoAlts.lgs",
                "defaultMessage": "Let's Get Set home page button",
            },
            "gac": {
                "id": "referrerHook.logoAlts.gac",
                "defaultMessage": "Get Ahead Colorado home page button",
            },
            "fircsummitresourcecenter": {
                "id": "referrerHook.logoAlts.fircsummitresourcecenter",
                "defaultMessage": "Firc Summit Resource Center",
            },
            "coBenefits": {
                "id": "referrerHook.logoAlts.coBenefits",
                "defaultMessage": "MyFriendBen home page button",
            },
            "dhs": {
                "id": "referrerHook.logoAlts.dhs",
                "defaultMessage": "Denver Human Services and MyFriendBen home page button",
            },
        },
        "logoFooterSource": {"default": " MFB_Logo"},
        "logoFooterAlt": {"default": {"id": "footer.logo.alt", "defaultMessage": "MFB Logo"}},
        "logoClass": {"default": "logo"},
        "twoOneOneLink": {
            "default": "https://nc211.org/?utm_source=myfriendben&utm_medium=inlink&utm_campaign=organic&utm_id=211mfb"
        },
        "shareLink": {"default": "https://screener.bennc.org"},
        "stepDirectory": {
            "default": [
                "zipcode",
                # the hhSize and hhData have to be consecutive
                "householdSize",
                "householdData",
                "hasExpenses",
                "householdAssets",
                "hasBenefits",
                "acuteHHConditions",
                "referralSource",
                "signUpInfo",
            ],
            "ccig": [
                "zipcode",
                "householdSize",
                "householdData",
                "hasExpenses",
                "householdAssets",
                "hasBenefits",
                "acuteHHConditions",
                "referralSource",
            ],
        },
    }

    footer_data = {
        "address_one": "201 W Main St.",
        "address_two": "Suite 100",
        "city": "Durham",
        "state": "NC",
        "zip_code": 27701,
        "email": "myfriendben@codethedream.org",
        "privacy_policy_link": "https://bennc.org/privacy-policy/",
    }

    feedback_links = {
        "survey": "https://airtable.com/app8EC0NO7FrnAMlP/pagiU2dMjYRofDxEn/form",
        "email": "mailto:myfriendben@codethedream.org",
    }
