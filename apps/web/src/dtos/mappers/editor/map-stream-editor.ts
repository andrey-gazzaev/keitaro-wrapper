import type { StreamEditor } from '@/models';
import type { StreamEditorDto } from '../../schemas/editor/stream-editor.schema';
import type { StreamOfferAddDto } from '../../schemas/editor/stream-offer-add.schema';
import { mapStreamGroup } from './map-stream-group';

/** Editor state from an editor JSON body. */
export function mapStreamEditor(dto: StreamEditorDto): StreamEditor {
  return {
    campaignId: dto.campaign_id,
    streams: dto.streams.map(mapStreamGroup),
  };
}

/** POST body that binds an offer to a stream. */
export function mapStreamOfferAddDto(streamId: number, offerId: number): StreamOfferAddDto {
  return {
    stream_id: streamId,
    offer_id: offerId,
  };
}
