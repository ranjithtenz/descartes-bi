#
#    Copyright (C) 2010  Roberto Rosario
#    This file is part of descartes-bi.
#
#    descartes-bi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    descartes-bi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with descartes-bi.  If not, see <http://www.gnu.org/licenses/>.
#

from django import forms
from django.utils.translation import ugettext_lazy as _
from models import FILTER_TYPE_DATE, FILTER_TYPE_COMBO, FILTER_TYPE_MONTH

class FilterForm(forms.Form):
    def __init__(self, filtersets, user, *args, **kwargs):
        #cannot move this from here until leading _ is removed
        from views import _get_user_filters_limits
        super(FilterForm, self).__init__(*args, **kwargs)
        for fset in filtersets.all():
            for f in fset.filterextra_set.order_by('order').all():
                if f.filter.type == FILTER_TYPE_DATE:
                    f.filter.execute_function()
                    self.fields[f.filter.name] = forms.DateField(('%m/%d/%Y',),
                    initial=f.filter.default, required=False,
                    label=f.filter.label,
                    widget=forms.DateInput(format='%m/%d/%Y',
                                           attrs={'size':'10'}))
                elif f.filter.type == FILTER_TYPE_COMBO:
                    results = _get_user_filters_limits(user)
                    #TODO: try this later on
                    #if f.filter in results and 'mask' in results[f.filter]:
                    try:
                        choices = list()
                        #TODO: change EVAL() to something safer
                        for choice in eval(f.filter.options, {}):
                            if choice[0] in results[f.filter]['mask']:
                                choices.append(choice)
                    except:
                        #No mask found, so all options are available
                        #TODO: change EVAL() to something safer
                        choices = eval(f.filter.options, {})

                    if f.filter in results:
                        if 'default' in results[f.filter]:
                            f.filter.default = results[f.filter]['default']
                            
                    self.fields[f.filter.name] = \
                    forms.ChoiceField(initial=f.filter.default, required=False,
                                    label=f.filter.label, choices = choices)
                elif f.filter.type == FILTER_TYPE_MONTH:
                    self.fields[f.filter.name] = \
                    forms.ChoiceField(initial=f.filter.default, required=False,
                    label=f.filter.label,
                    choices = (('1',_(u'January')),('2', _(u'February')),
                                ('3', _(u'March')),('4', _(u'April')),
                                ('5', _(u'May')),('6', _(u'June')),
                                ('7', _(u'July')),('8', _(u'August')),
                                ('9', _(u'September')),('10', _(u'October')),
                                ('11', _(u'November')),('12', _(u'December'))))

        self.fields['output_type'] = forms.ChoiceField(initial='chart',
                                    required=False, label=_(u'Format'),
                                    choices = (('chart', _(u'Chart')),
                                                ('grid', _(u'Table'))))
    class Media:
        js = ('js/filterform.js',)
    
