# V3: chemischer Basiskern

`kernel.py` ist eine instanzbasierte Bilanz aus Gas, Sternparzellen, Resten (Remnants) und Abfluss für **eine** wohlgemischte Zone. Es gibt keinen Singleton und keine freien Ressourcenbezeichner. Die illustrativen Modelle StellarLifecycle und TheChronicle bleiben unverändert (Befund F5).

- **Einheiten:** Masse in M☉, Zeit intern in Myr. `UNITS` rechnet Jahre, kyr und Gyr um (Orakel 7).
- **Elemente:** H, He, C, O, Si und REST; Metallizität Z = C + O + Si + REST (Befund N5).
- **Ertragskonvention:** Netto. Die neu synthetisierte Masse je gebildeter Sternmasse summiert sich zu 0; der Massendefekt wird nicht modelliert (dokumentierte baryonische Näherung).
  - Gesamtauswurf: E_i = m·(R·X_i + p_i); der Rest behält (1−R)·m mit Geburtszusammensetzung.
  - Tabellen mit Gesamtauswurf werden über `net_from_total` umgerechnet. Werden Gesamtwerte fälschlich als Nettowerte eingegeben, verletzt das die Summe 0 und wird abgelehnt.
- **Rückgabe** exakt zum Zeitpunkt t_Geburt + Lebensdauer, nie früher. Lebensdauer 0 bedeutet instantane Rückgabe.
- **Herkunft:** Jede Gasportion trägt eine Marke (`primordial`, `inflow:<name>`, `<Ertragsmodell>:star<k>`). Sternbildung und Abfluss entnehmen jede Marke anteilig.
- **Bilanz:** `budget()` = Gas + Sterne + Reste + Abfluss − Zufluss − Synthese, je Element konstant gleich dem Anfangsbestand.
- **Nichtnegativität:** Entnahmen über den Bestand hinaus und Ertragsmodelle mit negativem Auswurf für die gegebene Geburtszusammensetzung werden abgelehnt, bevor sich der Zustand ändert.

**Grenzen:**
- Nur synthetische Erträge.
- Eine Zone; Mehrzonen-Mischung folgt in V5.
- Keine Lebensdauer- und Ertragsabhängigkeit von Masse und Metallizität über das je Parzelle gewählte Modell hinaus.
- Keine Physik realer Sterne; Tabellen folgen in V4, erst nach Johanns OK.

**Tests:** `python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests`. Datei `test_v3_chem.py` enthält die Orakel 1–4 und 7 aus Plan §10.1 mit vorab von Hand hergeleiteten Werten.
