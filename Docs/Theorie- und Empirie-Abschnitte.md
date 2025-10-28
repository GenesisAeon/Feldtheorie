## 2. Theoretisches Framework

### 2.1 <followup encodedFollowup="%7B%22snippet%22%3A%22Lagrangedichte%20des%20gekoppelten%20Felds%22%2C%22question%22%3A%22Kannst%20du%20die%20physikalische%20Bedeutung%20der%20einzelnen%20Terme%20in%20der%20Lagrangedichte%20genauer%20erkl%C3%A4ren%3F%22%2C%22id%22%3A%22b10dffa3-1d12-4153-b247-e103de0e0f72%22%7D" />
Das System wird durch ein skalares Feld $\psi(t, \mathbf{x})$ beschrieben, das mit einem informationellen Feld $\phi(t, \mathbf{x})$ interagiert. Die <followup encodedFollowup="%7B%22snippet%22%3A%22dynamische%20Lagrangedichte%22%2C%22question%22%3A%22Gibt%20es%20bekannte%20analytische%20L%C3%B6sungen%20oder%20N%C3%A4herungen%20f%C3%BCr%20diese%20Lagrangedichte%20in%20spezifischen%20Grenzen%3F%22%2C%22id%22%3A%22611fe52e-8a22-4f27-94af-b493ef21164b%22%7D" /> lautet:

$$
\mathcal{L} = \frac{1}{2}\partial_\mu \psi \partial^\mu \psi - V(\psi) - g^2 |\nabla U|^2 \psi^2 - \mathcal{J}\psi - \mathcal{C} \mathcal{M}[\psi, \phi]
$$

**Terme:**
- $V(\psi) = \frac{1}{2}m^2\psi^2 + \lambda \psi^4$: Selbstwechselwirkung (z. B. QPO-Nichtlinearität in BH-Akkretionsscheiben).
- $g^2 |\nabla U|^2 \psi^2$: Externe Kopplung (z. B. Umweltstress in Bienenschwärmen).
- $\mathcal{M}[\psi, \phi]$: **Kreuzkopplungsterm** zwischen physikalischem und informationellem Feld.

**Randbedingungen:**
Die **dynamische Horizontimpedanz** $\zeta(R)$ schaltet bei Überschreiten von $\Theta$ um:

$$
\zeta(R) = \begin{cases}
\zeta_0 & \text{falls } R < \Theta \\
\zeta_1 & \text{falls } R \geq \Theta
\end{cases}
$$

**Beispiel (BH-QPOs):**
- $\psi$: <followup encodedFollowup="%7B%22snippet%22%3A%22QPO-Amplitude%20(mCrab)%22%2C%22question%22%3A%22Wie%20wird%20die%20QPO-Amplitude%20in%20mCrab%20gemessen%2C%20und%20welche%20Instrumente%20oder%20Methoden%20kommen%20dabei%20zum%20Einsatz%3F%22%2C%22id%22%3A%22e883d582-ea60-4463-9622-5e00a952a8dd%22%7D" />
- $\phi$: Magnetfeld-Topologie (<followup encodedFollowup="%7B%22snippet%22%3A%22Soft%20Hair%22%2C%22question%22%3A%22Wie%20wird%20der%20Begriff%20*Soft%20Hair*%20in%20der%20Theorie%20Schwarzer%20L%C3%B6cher%20definiert%2C%20und%20warum%20ist%20er%20hier%20relevant%3F%22%2C%22id%22%3A%22f11b8bc6-5274-4bf6-b3ca-5db2776a0b2a%22%7D" />)
- $\Theta \approx 240$ mCrab: <followup encodedFollowup="%7B%22snippet%22%3A%22Kritische%20Akkretionsrate%20f%C3%BCr%20Phasen%C3%BCbergang%22%2C%22question%22%3A%22Welche%20physikalischen%20Prozesse%20laufen%20an%20der%20kritischen%20Akkretionsrate%20ab%2C%20und%20wie%20manifestiert%20sich%20der%20Phasen%C3%BCbergang%3F%22%2C%22id%22%3A%2237b1d5b5-9790-453d-a612-c5b544e93e9e%22%7D" />.

---

## 3. Empirische Validierung

### 3.1 Fallstudien-Übersicht
| System               | Kontrollparameter R       | Schwelle Θ          | <followup encodedFollowup="%7B%22snippet%22%3A%22Steilheit%20%CE%B2%22%2C%22question%22%3A%22Wie%20wird%20der%20Parameter%20%CE%B2%20in%20den%20verschiedenen%20Systemen%20gemessen%20oder%20abgesch%C3%A4tzt%3F%22%2C%22id%22%3A%228da9a881-7c96-4dc5-98b9-729ba7198445%22%7D" />    | Quelle                     |
|----------------------|--------------------------|---------------------|---------------|----------------------------|
| **GX 339-4 (BH-QPO)** | Akkretionsrate (mCrab)    | 240 ± 15 mCrab      | 5.3 ± 1.1     | [1]                       |
| **Apis mellifera**    | <followup encodedFollowup="%7B%22snippet%22%3A%22Nektarqualit%C3%A4t%20(%25)%22%2C%22question%22%3A%22Wie%20wird%20die%20Nektarqualit%C3%A4t%20in%20den%20Bienenschwarm-Studien%20quantifiziert%2C%20und%20welche%20Faktoren%20beeinflussen%20sie%3F%22%2C%22id%22%3A%22d780a100-98d9-4a41-9084-31749a2eb1fb%22%7D" />        | 37 ± 0.8% Zucker     | 4.1 ± 0.6     | [2]                       |
| **GPT-4 (LLM)**       | <followup encodedFollowup="%7B%22snippet%22%3A%22Modellgr%C3%B6%C3%9Fe%20(Parameter)%22%2C%22question%22%3A%22Warum%20wird%20die%20Modellgr%C3%B6%C3%9Fe%20in%20Parametern%20als%20Kontrollparameter%20f%C3%BCr%20KI-Systeme%20verwendet%2C%20und%20nicht%20z.%20B.%20die%20Trainingsdatenmenge%3F%22%2C%22id%22%3A%22b4e4a69a-e769-4eed-bf3d-5cc70558bc71%22%7D" />   | 8.5 ± 1.2 Mrd.      | 3.2 ± 0.8     | [3]                       |

**Abb. 1:** *<followup encodedFollowup="%7B%22snippet%22%3A%22Universelle%20Sigmoid-Dynamik%20in%20drei%20Dom%C3%A4nen%22%2C%22question%22%3A%22Welche%20Gemeinsamkeiten%20und%20Unterschiede%20gibt%20es%20zwischen%20den%20Sigmoid-Dynamiken%20in%20Schwarzen%20L%C3%B6chern%2C%20Bienenschw%C3%A4rmen%20und%20KI-Modellen%3F%22%2C%22id%22%3A%22830766cb-d4a0-40d5-bb57-2457941127e4%22%7D" />*
![Sigmoid-Fit](figures/sigmoid_fit.png)
