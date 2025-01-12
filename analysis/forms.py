from django import forms

class ProbabilityForm(forms.Form):
    distribution = forms.ChoiceField(choices=[
        ('bernoulli', 'Bernoulli'),
        ('binomial', 'Binomial'),
        ('uniform', 'Uniform'),
        ('poisson', 'Poisson'),
        ('normal', 'Normal Continuous'),
        ('exponential', 'Exponential')
    ])
    p = forms.FloatField(required=False, label='p (Probability of Success)')
    n = forms.IntegerField(required=False, label='n (Number of Trials)')
    mean = forms.FloatField(required=False, label='Mean')
    std_dev = forms.FloatField(required=False, label='Standard Deviation')
    lambda_value = forms.FloatField(required=False, label='λ (Rate Parameter)')
