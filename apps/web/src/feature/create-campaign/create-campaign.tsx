import { useState, type FormEvent } from 'react';
import axios from 'axios';
import { useCreateCampaign } from '@/queries';
import { Stack } from '@/ui';
import styles from './create-campaign.module.css';

/** Form that creates one campaign. */
export function CreateCampaign() {
  const [name, setName] = useState('');
  const [country, setCountry] = useState('');
  const [offerId, setOfferId] = useState('');
  const createCampaign = useCreateCampaign();

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedName = name.trim();
    const trimmedCountry = country.trim();
    const parsedOfferId = positiveOfferId(offerId);

    if (trimmedName === '' || trimmedCountry === '' || parsedOfferId == null) {
      return;
    }

    createCampaign.mutate({
      name: trimmedName,
      country: trimmedCountry,
      offerId: parsedOfferId,
    });
  }

  return (
    <Stack as="form" variant="start" onSubmit={submit}>
      <label className={styles.field}>
        Название
        <input value={name} onChange={(event) => setName(event.target.value)} />
      </label>

      <label className={styles.field}>
        Гео-код
        <input value={country} onChange={(event) => setCountry(event.target.value)} />
      </label>

      <label className={styles.field}>
        Id оффера
        <input value={offerId} onChange={(event) => setOfferId(event.target.value)} />
      </label>

      <button type="submit" disabled={createCampaign.isPending}>
        Создать
      </button>

      {createCampaign.isSuccess && createCampaign.data ? (
        <p className="status">Кампания «{createCampaign.data.name}» создана.</p>
      ) : null}

      {createCampaign.isError ? <p className="status">{createFailure(createCampaign.error)}</p> : null}
    </Stack>
  );
}

function positiveOfferId(value: string): number | null {
  const trimmed = value.trim();

  if (!/^[1-9]\d*$/.test(trimmed)) {
    return null;
  }

  return Number(trimmed);
}

function createFailure(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return 'Keitaro не ответил.';
  }

  if (error.response?.status === 422) {
    return 'Проверьте название, страну и id оффера.';
  }

  if (error.response?.status === 409) {
    return 'В Keitaro нет домена, группы или источника.';
  }

  if (error.response?.status === 404) {
    return 'Оффер не найден.';
  }

  if (error.response?.status === 503) {
    return 'API Keitaro не настроен.';
  }

  return 'Keitaro не ответил.';
}
