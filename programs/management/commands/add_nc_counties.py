from django.core.management.base import BaseCommand
from programs.models import County
from screener.models import WhiteLabel


class Command(BaseCommand):
    help = "Adds NC counties"

    def get_white_label(self):
        return WhiteLabel.objects.get(code="nc")

    def handle(self, *args, **options):
        counties = [
            "Alamance County",
            "Alexander County",
            "Alleghany County",
            "Anson County",
            "Ashe County",
            "Avery County",
            "Beaufort County",
            "Bertie County",
            "Bladen County",
            "Brunswick County",
            "Buncombe County",
            "Burke County",
            "Cabarrus County",
            "Caldwell County",
            "Camden County",
            "Carteret County",
            "Caswell County",
            "Catawba County",
            "Chatham County",
            "Cherokee County",
            "Chowan County",
            "Clay County",
            "Cleveland County",
            "Columbus County",
            "Craven County",
            "Cumberland County",
            "Currituck County",
            "Dare County",
            "Davidson County",
            "Davie County",
            "Duplin County",
            "Durham County",
            "Edgecombe County",
            "Forsyth County",
            "Franklin County",
            "Gaston County",
            "Gates County",
            "Graham County",
            "Granville County",
            "Greene County",
            "Guilford County",
            "Halifax County",
            "Harnett County",
            "Haywood County",
            "Henderson County",
            "Hertford County",
            "Hoke County",
            "Hyde County",
            "Iredell County",
            "Jackson County",
            "Johnston County",
            "Jones County",
            "Lee County",
            "Lenoir County",
            "Lincoln County",
            "McDowell County",
            "Macon County",
            "Madison County",
            "Martin County",
            "Mecklenburg County",
            "Mitchell County",
            "Montgomery County",
            "Moore County",
            "Nash County",
            "New Hanover County",
            "Northampton County",
            "Onslow County",
            "Orange County",
            "Pamlico County",
            "Pasquotank County",
            "Pender County",
            "Perquimans County",
            "Person County",
            "Pitt County",
            "Polk County",
            "Randolph County",
            "Richmond County",
            "Robeson County",
            "Rockingham County",
            "Rowan County",
            "Rutherford County",
            "Sampson County",
            "Scotland County",
            "Stanly County",
            "Stokes County",
            "Surry County",
            "Swain County",
            "Transylvania County",
            "Tyrrell County",
            "Union County",
            "Vance County",
            "Wake County",
            "Warren County",
            "Washington County",
            "Watauga County",
            "Wayne County",
            "Wilkes County",
            "Wilson County",
            "Yadkin County",
            "Yancey County",
        ]

        white_label = self.get_white_label()
        if not white_label:
            self.stdout.write(self.style.WARNING(f"NC White label does not exist"))
            return
        
        for county in counties:
            County.objects.get_or_create(name=county, white_label=white_label)

        self.stdout.write(self.style.SUCCESS(f"Added NC counties"))