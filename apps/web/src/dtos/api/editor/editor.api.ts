import type { Offer, StreamEditor } from '@/models';
import { api } from '../../http';
import { mapOffer } from '../../mappers/editor/map-offer';
import { mapStreamEditor, mapStreamOfferAddDto } from '../../mappers/editor/map-stream-editor';
import { offerSchema } from '../../schemas/editor/offer.schema';
import { streamEditorSchema } from '../../schemas/editor/stream-editor.schema';

/** Loads and changes the stream editor for one campaign. */
export class EditorApi {
  /** Stored editor. Streams are empty before the first fetch. */
  public async load(campaignId: number): Promise<StreamEditor> {
    const { data } = await api.get(`/campaigns/${campaignId}/editor`);

    return mapStreamEditor(streamEditorSchema.parse(data));
  }

  /** Import flows from Keitaro and return the editor. */
  public async fetch(campaignId: number): Promise<StreamEditor> {
    const { data } = await api.post(`/campaigns/${campaignId}/editor/fetch`);

    return mapStreamEditor(streamEditorSchema.parse(data));
  }

  /** Offer name for this id. Rejects when Keitaro has no such offer. */
  public async lookup(campaignId: number, offerId: number): Promise<Offer> {
    const { data } = await api.get(`/campaigns/${campaignId}/editor/available-offers/${offerId}`);

    return mapOffer(offerSchema.parse(data));
  }

  /** Bind an offer to a stream and return the editor. */
  public async add(campaignId: number, streamId: number, offerId: number): Promise<StreamEditor> {
    const { data } = await api.post(
      `/campaigns/${campaignId}/editor/offers`,
      mapStreamOfferAddDto(streamId, offerId),
    );

    return mapStreamEditor(streamEditorSchema.parse(data));
  }

  /** Archive one live binding and return the editor. */
  public async remove(campaignId: number, bindingId: number): Promise<StreamEditor> {
    const { data } = await api.post(`/campaigns/${campaignId}/editor/offers/${bindingId}/remove`);

    return mapStreamEditor(streamEditorSchema.parse(data));
  }

  /** Restore one deleted binding and return the editor. */
  public async bringBack(campaignId: number, bindingId: number): Promise<StreamEditor> {
    const { data } = await api.post(`/campaigns/${campaignId}/editor/offers/${bindingId}/bring-back`);

    return mapStreamEditor(streamEditorSchema.parse(data));
  }

  /** Fix one offer's share and return the editor. */
  public async pin(campaignId: number, bindingId: number, share: string): Promise<StreamEditor> {
    const { data } = await api.post(`/campaigns/${campaignId}/editor/offers/${bindingId}/pin`, { share });

    return mapStreamEditor(streamEditorSchema.parse(data));
  }

  /** Return one offer to the split and return the editor. */
  public async unpin(campaignId: number, bindingId: number): Promise<StreamEditor> {
    const { data } = await api.post(`/campaigns/${campaignId}/editor/offers/${bindingId}/unpin`);

    return mapStreamEditor(streamEditorSchema.parse(data));
  }

  /** Replace the live flow's offers and return the editor. */
  public async push(campaignId: number, streamId: number): Promise<StreamEditor> {
    const { data } = await api.post(`/campaigns/${campaignId}/editor/streams/${streamId}/push`);

    return mapStreamEditor(streamEditorSchema.parse(data));
  }

  /** Drop unpublished bindings, restore the snapshot, and return the editor. */
  public async cancel(campaignId: number, streamId: number): Promise<StreamEditor> {
    const { data } = await api.post(`/campaigns/${campaignId}/editor/streams/${streamId}/cancel`);

    return mapStreamEditor(streamEditorSchema.parse(data));
  }
}

/** Shared editor client. */
export const editorApi = new EditorApi();
