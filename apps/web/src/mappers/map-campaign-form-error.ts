import { CampaignCreateError } from '@/models';
import type { CampaignFormErrorVm } from '@/view-models';

const EMPTY_FORM_ERROR: CampaignFormErrorVm = {
  name: '',
  country: '',
  offerId: '',
  form: '',
};

const CHECK_ALL = 'Проверьте название, страну и id оффера.';

/** Field and form messages for a campaign create failure. Every string is empty when `error` is absent. */
export function mapCampaignFormError(error: unknown): CampaignFormErrorVm {
  if (!(error instanceof CampaignCreateError)) {
    if (error == null) {
      return EMPTY_FORM_ERROR;
    }

    return { ...EMPTY_FORM_ERROR, form: 'Keitaro не ответил.' };
  }

  if (error.kind === 'invalid') {
    return invalidMessages(error.fields);
  }

  if (error.kind === 'missingOffer') {
    return { ...EMPTY_FORM_ERROR, offerId: 'Оффер не найден.' };
  }

  if (error.kind === 'missingSetup') {
    return { ...EMPTY_FORM_ERROR, form: 'В Keitaro нет домена, группы или источника.' };
  }

  if (error.kind === 'notConfigured') {
    return { ...EMPTY_FORM_ERROR, form: 'API Keitaro не настроен.' };
  }

  return { ...EMPTY_FORM_ERROR, form: 'Keitaro не ответил.' };
}

function invalidMessages(fields: CampaignCreateError['fields']): CampaignFormErrorVm {
  if (fields.length === 0) {
    return {
      name: CHECK_ALL,
      country: CHECK_ALL,
      offerId: CHECK_ALL,
      form: '',
    };
  }

  return {
    name: fields.includes('name') ? 'Проверьте название.' : '',
    country: fields.includes('country') ? 'Проверьте страну.' : '',
    offerId: fields.includes('offerId') ? 'Проверьте id оффера.' : '',
    form: '',
  };
}
