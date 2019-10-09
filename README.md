Carousels
========= 

Library-specific configuration settings for the OPAC carousels are managed in `config.ini`.

##### Configurable Settings
- Number of items to display
- Items statuses to display (Default is *Available*)
- Shelving locations to search
- Speed of carousel rotation
- Enable/Disable cover image shadow

## Configuration Variables & Build Automation

**Evergreen Copy Statuses**

| ID | Status |
| --- | --- |
| 0 | Available |
| 1 | Checked Out |
| 2 | Bindery |
| 3 | Lost |
| 4 | Missing |
| 5 | In Process |
| 6 | In Transit |
| 7 | Reshelving |
| 8 | On Holds Shelf |
| 9 | On Order |
| 10 | ILL |
| 11 | Cataloging |
| 12 | Reserves |
| 13 | Discard/Weed |
| 14 | Damaged |
| 15 | On Reservation Shelf |
| 16 | Long Overdue |
| 17 | Lost and Paid |

*Available* is the default setting. If desired, a selection of statuses can be configured.

*Reshelving* status is indicative of available items that have recently been returned, but have yet to be shelved. This would be an ideal additional status to include in a book carousel.

An alternative interpretation of item status could be: thinking about *On Holds Shelf* or *Checked out* as items that are popular in your community. Or, thinking about *In Process* or *On Order* as a marketing opportunity for upcoming new materials.

**COOL Shelving Locations**

List available upon request

**How are materials selected for the carousel?**

It's a combination of both the library-specific configuration in `config.ini` and the [Evergreen's SuperCat](http://docs.evergreen-ils.org/3.1/_records.html) capabilities, specifically the recent records feed.

**How often is my carousel updated?**

It depends. The script to generate the carousels runs every 30 minutes (via a cron job on the server). When the script runs, it requests all of the newly added or recently edited bibliographic records. If your library has copies attached to any of the newly added or edited bib records, and: (1) those copies are assigned to any of the shelving locations defined in `config.ini`, and (2) the copy is in one of the copy statuses defined in `config.ini`, and (3) the copy has a valid cover image associated with it, it will appear in your carousel. If no *new* copies match these criterion, the carousel will remain unchanged for another 30 minutes.
