from programs.programs.categories.base import CategoryCap, ProgramCategoryCapCalculator


class PreschoolCategoryCap(ProgramCategoryCapCalculator):
    static_caps = [CategoryCap(["dpp", "upk", "chs"], max=8_640, member_cap=True)]
