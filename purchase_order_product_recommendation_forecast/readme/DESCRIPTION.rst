This module extends the purchase product recommendator to predict the increment of
the recommendator quantities comparing to past periods.

So when we evaluate a period in the recommendator, this module analyze the same period
for the given year of refences a computes the increment for the immediately next period
of the same length.

With those increments (or decreases) we can deduce and forecast recommended quantities
making a simple linear progression.

An example to illustrate this. I want to forecast sales for April and I'm going to
analyze sales on March, but I want to forecast how the recommended products behave
from this period to the next one. I also want to analyze, a normal year as 2020 was
very irregular due to pandemy, so I'll use 2019 as my year of reference.

The wizard will take the deliveries from March 2019 and then the deliveries from
April 2019 and then it will compute the increment between those two periods.

With that increment, the wizard will analyze the deliveries for March of the present
year and then it will apply the increment computed for 2019 and those will be the
quantities that we'll be recommending according to the current stock.
