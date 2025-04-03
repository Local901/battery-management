<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

### 3.1.4

- Fix schedule retrieval in minimum charge percentage config.

### 3.1.3

- Fix mcp handle code. It forced it to 0 if present in the schedule.

### 3.1.1

- Fix code

## 3.1.0

- Add minimum charge limit to schedule.

### 3.0.2

- Fix discharge limit

### 3.0.1

- Fix config

## 3.0.0

- Update schedule.
  - Auto loop schedule.
  - Default to none.
- Discharge limit

### 2.1.0

- Add the option to loop the schedule.

### 2.0.4

- Re-enable resubmitting of modbus states.
- calculate day correctly.

### 2.0.3

- Fix schedule implementation.
  - allow 'o' or 'O' to be used together with '0'.

### 2.0.2

- Remove testing prints.
- Update Docs.

### 2.0.1

- Fix linting.

## 2.0.0

- Change the schedule to be a list of hours for the current day and the next.

## 1.0.0

- First release.
