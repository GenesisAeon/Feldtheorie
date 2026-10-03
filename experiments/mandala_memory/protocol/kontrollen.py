"""Independent standard-library controls; no imports from production repositories."""
from fractions import Fraction as F
import json
import math
from pathlib import Path


def trajectory(inputs, initial=0.0, decay=0.5):
    x = initial
    result = []
    for value in inputs:
        x = decay * x + value
        result.append(x)
    return result


def matrix(n, modules, gamma, c=None):
    size = n // modules
    return [[F(0) if i == j else gamma / (n-1) if modules == 1
             else gamma*(1-c)/(size-1) if i//size == j//size
             else gamma*c/(n-size) for j in range(n)] for i in range(n)]


def run():
    result = {}
    delays = [0, 1, 2, 4, 8]
    values = []
    for d in delays:
        expected = F(1, 2**d)
        assert trajectory([1]+[0]*d)[-1] == float(expected)
        assert trajectory([-1]+[0]*d)[-1] == -float(expected)
        values.append(str(expected))
    result['K1'] = dict(delays=delays, positive_states=values)
    normal_cdf = lambda z: (1+math.erf(z/math.sqrt(2)))/2
    accuracy = [normal_cdf(float(F(1, 2**d))/0.25) for d in delays]
    assert all(accuracy[i] > accuracy[i+1] for i in range(len(accuracy)-1))
    result['K2'] = dict(sigma=0.25, bayes_accuracy=accuracy)
    assert trajectory([0]*8, initial=0)[-1] == 0
    result['K3'] = dict(reset_state=0, bayes_accuracy=0.5)
    a = F(1, 8)
    first, second = (a, F(0)), (F(0), a)
    assert first != second and sum(first) == sum(second)
    result['K4'] = dict(equal_sum=str(sum(first)), full_states_distinct=True)
    scaled = [normal_cdf(float(F(1, 2**d))*1000/250) for d in delays]
    assert scaled == accuracy
    result['K5'] = dict(amplitude_scale=1000, same_accuracy=True)
    decode = lambda x: 0 if x[0] > x[1] else 1
    inputs = [(1, 0), (0, 1)]
    swapped = [x[::-1] for x in inputs]
    assert [decode(x) for x in swapped] == [1, 0]
    assert [decode(x[::-1]) for x in swapped] == [0, 1]
    result['K6'] = dict(frozen_accuracy=0, remapped_accuracy=1, invertible=True)
    uniform = matrix(12, 1, F(4, 5))
    modular = matrix(12, 3, F(4, 5), F(8, 11))
    assert uniform == modular
    assert all(sum(row) == F(4, 5) for row in uniform)
    result['K7'] = dict(exact_matrix_equality=True, row_sum='4/5', off_diagonal=str(uniform[0][1]))
    q = F(1, 2)+F(1, 2)*F(4, 5)
    x, z = 0.2, 0.7
    initial_distance = abs(x-z)
    for k in range(1, 11):
        x = 0.5*x+0.5*math.tanh(0.8*x)
        z = 0.5*z+0.5*math.tanh(0.8*z)
        assert abs(x-z) <= float(q**k)*initial_distance+1e-15
    result['K8'] = dict(q=str(q), q_power_10=float(q**10), sample_distance=abs(x-z), bound=float(q**10)*initial_distance)
    stimuli = [1, 0, 0, 0, 0]
    whole = trajectory(stimuli)
    prefix = trajectory(stimuli[:2])
    continued = prefix+trajectory(stimuli[2:], initial=prefix[-1])
    reset = prefix+trajectory(stimuli[2:])
    assert whole == continued and whole != reset
    result['K9'] = dict(whole=whole, continued=continued, reset=reset)
    return dict(status='passed', independent_control_groups=9,
                scope='analytical/exact controls and one numerical contraction example; no production tests',
                results=result)


if __name__ == '__main__':
    output = run()
    target = Path(__file__).with_name('kontrollen_ergebnisse.json')
    target.write_text(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(output, indent=2))
