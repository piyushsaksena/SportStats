# SportStats — Data Dictionary

> Automatically generated from SQLAlchemy ORM metadata and database schema specifications.

## 1. Schema Overview

The SportStats relational model consists of **23 tables** and **5 analytical views** structured into 4 logical groups (Figure 2 in research report):
- **Tournament Information & Tracking**: `sport`, `discipline`, `country`, `venue`, `tournament`, `tournament_edition`, `stage`, `match_event`, `match_side`, `olympic_result`
- **Participant Information**: `participant`, `player_profile`, `team_profile`, `team_membership`, `edition_participant`
- **Performance Statistics**: `metric_definition`, `performance_stat`
- **Rankings, Records & Provenance**: `ranking_snapshot`, `ranking_entry`, `record_entry`, `source`, `ingestion_run`, `data_quality_issue`

---

## 2. Metric Catalogue Summary (Figure 3 Depth of Statistics)

| Sport Code | Sport Name | Total Metrics Tracked | Report Figure 3 Target | Status |
|---|---|---|---|---|
| `cricket` | Cricket | **10** | 10 | ✅ Exact Match |
| `football` | Football | **10** | 10 | ✅ Exact Match |
| `badminton` | Badminton | **9** | 9 | ✅ Exact Match |
| `basketball` | Basketball | **10** | 10 | ✅ Exact Match |
| `tennis` | Tennis | **10** | 10 | ✅ Exact Match |
| `kabaddi` | Kabaddi | **10** | 10 | ✅ Exact Match |
| `olympic` | Olympic | **10** | 10 | ✅ Exact Match |

**Total Metrics across all sports**: **69**

---

## 3. Relational Tables

### Table: `country`
*ISO3 country reference registry.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `iso3` | `VARCHAR(3)` |  | **NOT NULL** | - | - |
| `name` | `VARCHAR(128)` |  | **NOT NULL** | - | - |
| `continent` | `VARCHAR(32)` |  | NULL | - | - |

### Table: `data_quality_issue`
*Itemized row validation errors and anomaly flags.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `ingestion_run_id` | `VARCHAR(36)` |  | NULL | FK -> `ingestion_run.id` | - |
| `table_name` | `VARCHAR(64)` |  | **NOT NULL** | - | - |
| `row_ref` | `VARCHAR(128)` |  | NULL | - | - |
| `severity` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `rule_code` | `VARCHAR(32)` |  | **NOT NULL** | - | - |
| `message` | `TEXT` |  | **NOT NULL** | - | - |
| `created_at` | `DATETIME` |  | **NOT NULL** | - | - |

### Table: `discipline`
*Sub-disciplines (e.g. Athletics, Swimming under Olympic Sports).*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `sport_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `sport.id` | - |
| `code` | `VARCHAR(32)` |  | **NOT NULL** | - | - |
| `name` | `VARCHAR(64)` |  | **NOT NULL** | - | - |

### Table: `edition_participant`
*Participants enrolled in a tournament edition with seeds and final positions.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `edition_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `tournament_edition.id` | - |
| `participant_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `participant.id` | - |
| `seed` | `INTEGER` |  | NULL | - | - |
| `group_label` | `VARCHAR(16)` |  | NULL | - | - |
| `final_position` | `INTEGER` |  | NULL | - | - |

### Table: `ingestion_run`
*Audit log for batch data collection and validation runs.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `source_id` | `VARCHAR(36)` |  | NULL | FK -> `source.id` | - |
| `started_at` | `DATETIME` |  | **NOT NULL** | - | - |
| `finished_at` | `DATETIME` |  | NULL | - | - |
| `status` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `rows_in` | `INTEGER` |  | **NOT NULL** | - | - |
| `rows_loaded` | `INTEGER` |  | **NOT NULL** | - | - |
| `rows_rejected` | `INTEGER` |  | **NOT NULL** | - | - |
| `log` | `TEXT` |  | NULL | - | - |

### Table: `match_event`
*Individual match, fixture, or event contest.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `edition_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `tournament_edition.id` | - |
| `stage_id` | `VARCHAR(36)` |  | NULL | FK -> `stage.id` | - |
| `sport_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `sport.id` | - |
| `discipline_id` | `VARCHAR(36)` |  | NULL | FK -> `discipline.id` | - |
| `scheduled_at` | `DATETIME` |  | **NOT NULL** | - | - |
| `venue_id` | `VARCHAR(36)` |  | NULL | FK -> `venue.id` | - |
| `status` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `winner_participant_id` | `VARCHAR(36)` |  | NULL | FK -> `participant.id` | - |
| `is_draw` | `BOOLEAN` |  | **NOT NULL** | - | - |
| `result_summary` | `TEXT` |  | NULL | - | - |
| `source_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `source.id` | - |
| `is_sample` | `BOOLEAN` |  | **NOT NULL** | - | - |

### Table: `match_side`
*Contestant performance and score details per match.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `match_event_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `match_event.id` | - |
| `participant_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `participant.id` | - |
| `side_index` | `INTEGER` |  | **NOT NULL** | - | - |
| `score_primary` | `NUMERIC(10, 2)` |  | NULL | - | - |
| `score_detail` | `JSON` |  | NULL | - | - |
| `is_winner` | `BOOLEAN` |  | NULL | - | - |

### Table: `metric_definition`
*Statistical metric definitions catalogue across sports.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `sport_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `sport.id` | - |
| `code` | `VARCHAR(64)` |  | **NOT NULL** | - | - |
| `name` | `VARCHAR(128)` |  | **NOT NULL** | - | - |
| `unit` | `VARCHAR(32)` |  | **NOT NULL** | - | - |
| `category` | `VARCHAR(32)` |  | **NOT NULL** | - | - |
| `aggregation` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `formula` | `TEXT` |  | NULL | - | - |
| `higher_is_better` | `BOOLEAN` |  | NULL | - | - |
| `description` | `TEXT` |  | NULL | - | - |

### Table: `olympic_result`
*Olympic event placements, medal awards, times, and records.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `edition_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `tournament_edition.id` | - |
| `discipline_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `discipline.id` | - |
| `event_name` | `VARCHAR(128)` |  | **NOT NULL** | - | - |
| `participant_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `participant.id` | - |
| `rank` | `INTEGER` |  | NULL | - | - |
| `medal` | `VARCHAR(16)` |  | NULL | - | - |
| `result_value` | `NUMERIC(10, 3)` |  | NULL | - | - |
| `result_unit` | `VARCHAR(32)` |  | NULL | - | - |
| `is_world_record` | `BOOLEAN` |  | **NOT NULL** | - | - |
| `is_olympic_record` | `BOOLEAN` |  | **NOT NULL** | - | - |

### Table: `participant`
*Universal participant entity representing teams, players, and athletes.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `type` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `name` | `VARCHAR(128)` |  | **NOT NULL** | - | - |
| `country_id` | `VARCHAR(36)` |  | NULL | FK -> `country.id` | - |
| `sport_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `sport.id` | - |
| `external_ids` | `JSON` |  | NULL | - | - |
| `is_sample` | `BOOLEAN` |  | **NOT NULL** | - | - |

### Table: `performance_stat`
*Atomic performance statistics linked to participants and editions.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `participant_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `participant.id` | - |
| `edition_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `tournament_edition.id` | - |
| `match_event_id` | `VARCHAR(36)` |  | NULL | FK -> `match_event.id` | - |
| `metric_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `metric_definition.id` | - |
| `value` | `NUMERIC(14, 4)` |  | **NOT NULL** | - | - |
| `scope` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `source_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `source.id` | - |
| `is_sample` | `BOOLEAN` |  | **NOT NULL** | - | - |

### Table: `player_profile`
*Individual player profile details (birth date, position, gender).*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `participant_id` | `VARCHAR(36)` | ✅ | **NOT NULL** | FK -> `participant.id` | - |
| `full_name` | `VARCHAR(128)` |  | **NOT NULL** | - | - |
| `birth_date` | `DATE` |  | NULL | - | - |
| `gender` | `VARCHAR(16)` |  | NULL | - | - |
| `role_or_position` | `VARCHAR(64)` |  | NULL | - | - |

### Table: `ranking_entry`
*Rank positions of participants within snapshots.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `snapshot_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `ranking_snapshot.id` | - |
| `participant_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `participant.id` | - |
| `rank` | `INTEGER` |  | **NOT NULL** | - | - |
| `points` | `NUMERIC(12, 2)` |  | NULL | - | - |

### Table: `ranking_snapshot`
*Official ranking snapshots published at specific dates.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `sport_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `sport.id` | - |
| `ranking_system` | `VARCHAR(64)` |  | **NOT NULL** | - | - |
| `category` | `VARCHAR(64)` |  | **NOT NULL** | - | - |
| `as_of_date` | `DATE` |  | **NOT NULL** | - | - |
| `source_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `source.id` | - |

### Table: `record_entry`
*All-time milestones and historical records.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `sport_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `sport.id` | - |
| `record_type` | `VARCHAR(32)` |  | **NOT NULL** | - | - |
| `metric_id` | `VARCHAR(36)` |  | NULL | FK -> `metric_definition.id` | - |
| `description` | `TEXT` |  | **NOT NULL** | - | - |
| `holder_participant_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `participant.id` | - |
| `value` | `NUMERIC(14, 4)` |  | NULL | - | - |
| `achieved_on` | `DATE` |  | NULL | - | - |
| `edition_id` | `VARCHAR(36)` |  | NULL | FK -> `tournament_edition.id` | - |
| `source_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `source.id` | - |

### Table: `source`
*Official and secondary data sources documenting complete data provenance.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `organisation` | `VARCHAR(128)` |  | **NOT NULL** | - | - |
| `name` | `VARCHAR(128)` |  | **NOT NULL** | - | - |
| `url` | `VARCHAR(512)` |  | **NOT NULL** | - | - |
| `access_method` | `VARCHAR(32)` |  | **NOT NULL** | - | - |
| `tier` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `terms_note` | `TEXT` |  | NULL | - | - |
| `retrieved_at` | `DATETIME` |  | **NOT NULL** | - | - |
| `is_verified` | `BOOLEAN` |  | **NOT NULL** | - | - |

### Table: `sport`
*Reference catalog of tracked sports disciplines.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `code` | `VARCHAR(32)` |  | **NOT NULL** | - | - |
| `name` | `VARCHAR(64)` |  | **NOT NULL** | - | - |
| `is_team_sport` | `BOOLEAN` |  | **NOT NULL** | - | - |
| `is_individual_sport` | `BOOLEAN` |  | **NOT NULL** | - | - |
| `notes` | `TEXT` |  | NULL | - | - |
| `created_at` | `DATETIME` |  | **NOT NULL** | - | - |
| `updated_at` | `DATETIME` |  | **NOT NULL** | - | - |

### Table: `stage`
*Tournament round or stage (group, knockout, heats, final).*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `edition_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `tournament_edition.id` | - |
| `name` | `VARCHAR(64)` |  | **NOT NULL** | - | - |
| `order_index` | `INTEGER` |  | **NOT NULL** | - | - |
| `type` | `VARCHAR(16)` |  | **NOT NULL** | - | - |

### Table: `team_membership`
*Player-to-team rosters per edition or season.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `team_participant_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `participant.id` | - |
| `player_participant_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `participant.id` | - |
| `edition_id` | `VARCHAR(36)` |  | NULL | FK -> `tournament_edition.id` | - |
| `role` | `VARCHAR(64)` |  | NULL | - | - |

### Table: `team_profile`
*Team profile details (national, franchise, club).*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `participant_id` | `VARCHAR(36)` | ✅ | **NOT NULL** | FK -> `participant.id` | - |
| `team_type` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `short_code` | `VARCHAR(16)` |  | NULL | - | - |

### Table: `tournament`
*High-level recurring tournaments and championships.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `sport_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `sport.id` | - |
| `discipline_id` | `VARCHAR(36)` |  | NULL | FK -> `discipline.id` | - |
| `name` | `VARCHAR(128)` |  | **NOT NULL** | - | - |
| `governing_body` | `VARCHAR(64)` |  | **NOT NULL** | - | - |
| `gender` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `level` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `frequency_years` | `INTEGER` |  | NULL | - | - |
| `notes` | `TEXT` |  | NULL | - | - |

### Table: `tournament_edition`
*Specific editions of tournaments with dates, host venues, and winners (Table 2).*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `tournament_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `tournament.id` | - |
| `edition_label` | `VARCHAR(64)` |  | **NOT NULL** | - | - |
| `year` | `INTEGER` |  | **NOT NULL** | - | - |
| `host_country_id` | `VARCHAR(36)` |  | NULL | FK -> `country.id` | - |
| `host_city` | `VARCHAR(64)` |  | NULL | - | - |
| `start_date` | `DATE` |  | **NOT NULL** | - | - |
| `end_date` | `DATE` |  | **NOT NULL** | - | - |
| `status` | `VARCHAR(16)` |  | **NOT NULL** | - | - |
| `participant_count` | `INTEGER` |  | **NOT NULL** | - | - |
| `format_description` | `TEXT` |  | NULL | - | - |
| `matches_or_events_count` | `INTEGER` |  | NULL | - | - |
| `winner_participant_id` | `VARCHAR(36)` |  | NULL | FK -> `participant.id` | - |
| `runner_up_participant_id` | `VARCHAR(36)` |  | NULL | FK -> `participant.id` | - |
| `source_id` | `VARCHAR(36)` |  | **NOT NULL** | FK -> `source.id` | - |
| `is_sample` | `BOOLEAN` |  | **NOT NULL** | - | - |

### Table: `venue`
*Host stadiums and arenas.*

| Column Name | Type | PK | Nullable | FK / Constraints | Description |
|---|---|---|---|---|---|
| `id` | `VARCHAR(36)` | ✅ | **NOT NULL** | - | - |
| `name` | `VARCHAR(128)` |  | **NOT NULL** | - | - |
| `city` | `VARCHAR(64)` |  | **NOT NULL** | - | - |
| `country_id` | `VARCHAR(36)` |  | NULL | FK -> `country.id` | - |
| `capacity` | `INTEGER` |  | NULL | - | - |

---

## 4. Analytical Views (Section 6.8)

### View: `v_tournament_tracking`
*Tracking view of upcoming, ongoing, and completed tournament editions with winners.*

### View: `v_edition_summary`
*One-row summary per edition with participant count, match counts, and champion.*

### View: `v_participant_edition_totals`
*Aggregated metric totals and averages per participant per tournament edition.*

### View: `v_win_loss_record`
*Matches played, wins, losses, draws, win percentage, and loss percentage.*

### View: `v_previous_winners`
*Historical tournament champions and runners-up across completed editions.*
