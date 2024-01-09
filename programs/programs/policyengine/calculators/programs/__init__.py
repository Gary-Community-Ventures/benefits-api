import programs.programs.policyengine.calculators.programs.member as member
import programs.programs.policyengine.calculators.programs.spm as spm
import programs.programs.policyengine.calculators.programs.tax as tax


member_calculators = {
    'wic': member.Wic,
    'medicaid': member.Medicaid,
    'pell_grant': member.PellGrant,
    'ssi': member.Ssi,
    'andcs': member.AidToTheNeedyAndDisabled,
    'oap': member.OldAgePension,
    'chp': member.Chp,
}

spm_unit_calculators = {
    'acp': spm.Acp,
    'lifeline': spm.Lifeline,
    'nslp': spm.SchoolLunch,
    'snap': spm.Snap,
    'tanf': spm.Tanf,
}

tax_unit_calculators = {
    'eitc': tax.Eitc,
    'coeitc': tax.Coeitc,
    'ctc': tax.Ctc,
    'coctc': tax.Coctc,
}
