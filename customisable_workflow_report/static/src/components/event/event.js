/** @odoo-module **/

import { Component, useRef, useState, onWillUpdateProps } from "@odoo/owl";
import { FileUploader } from "@web/views/fields/file_handler";
import { Avatar } from "@mail/views/web/fields/avatar/avatar";
import { useBus, useService } from "@web/core/utils/hooks";
import { useFileViewer } from "@web/core/file_viewer/file_viewer_hook";
import { FormViewDialog } from '@web/views/view_dialogs/form_view_dialog';
const { DateTime } = luxon;

export class Event extends Component {
    static components = { FileUploader, Avatar };
    setup() {
        super.setup();
        this.uploadFileInput = useRef("uploadFileInput");
        this.uploadService = useService("file_upload");
        this.uiService = useService("ui");
        this.dialogService = useService("dialog");
        this.store = useService("mail.store");
        this.fileViewer = useFileViewer();
        useBus(
            this.uploadService.bus,
            "FILE_UPLOAD_LOADED",
            (ev) => {
                this.props.reloadGroug();
                this.uiService.unblock();
            },
        );
        useBus(
            this.uploadService.bus,
            "FILE_UPLOAD_ERROR",
            () => {
                this.uiService.unblock();
            },
        );
        onWillUpdateProps((nextProps ) => {
            this.eventState.data = this._build_state(nextProps.event);
        });
        this.downloadRef = useRef("download");
        var event = this.props.event;
        this.eventState = useState({data: this._build_state(event)});
        this.actionHover = useState({isSourceHovered: false, isResultHovered: false});
    }
    onUpload() {
        // Trigger the input to select a file
        this.uploadFileInput.el.click();
    }
    signOrValidate() {
        var event = this.eventState.data;
        var title = ""
        if(event.type == 'signature'){
            title = "Signez ou rejetez: ";
        }
        else if(event.type == 'validation'){
            title = "Validez ou rejetez: ";
        }
        title += this.props.group.group[1];
        this.dialogService.add(
            FormViewDialog, {
                title: title,
                resModel: event.document_model,
                resId: event.reference,
                preventEdit: true,
                preventCreate: true
            },
            { onClose: () => this.props.reloadGroug() }
        );
    }
    async onInputChange(ev) {
        var event = this.eventState.data;
        if (!ev.target.files) {
            return;
        }
        this.uiService.block();
        this.uploadService.upload(
            "/web/binary/upload_given_document_attachment",
            ev.target.files,
            {
                buildFormData: (formData) => {
                    formData.append("model", event.document_model);
                    formData.append("id", event.reference);
                },
            },
        );
        ev.target.value = "";
    }
    downloadSource() {
        var event = this.eventState.data;
        var attachement_id = false;
        if(event.source_attachment != false){
            attachement_id = event.source_attachment[0]
        }
        if(attachement_id != false){
            const downloadLink = document.createElement('a');
            var downloadUrl = `/web/content/ir.attachment/${attachement_id}/datas?download=true`;
            downloadLink.setAttribute('href', downloadUrl);
            downloadLink.setAttribute('download','');
            downloadLink.click();
        }
        
    }
    downloadResult() {
        var event = this.eventState.data;
        var attachement_id = false;
        // For signature only expose PDF
        if(event.type == 'signature'){
            attachement_id = event.result_attachment_pdf[0]
        }
        else if(event.result_attachment != false){
            attachement_id = event.result_attachment[0]
        }
        if(attachement_id != false){
            const downloadLink = document.createElement('a');
            var downloadUrl = `/web/content/ir.attachment/${attachement_id}/datas?download=true`;
            downloadLink.setAttribute('href', downloadUrl);
            downloadLink.setAttribute('download','');
            downloadLink.click();
        }
    }
    previewResult() {
        var event = this.eventState.data;
        if(event.result_previewable == false){
            return
        }
        var attachment_id;
        var attachment_filename;
        var mimetype;
        var attachmentName = this.props.group.group[1];
        if (!attachment_id){
            attachment_id = event.result_attachment_pdf[0];
            attachment_filename = event.result_attachment_pdf[1];
        }
        if (!attachment_id){
            attachment_id = event.result_attachment[0];
            attachment_filename = event.result_attachment[0];
        }
        if (event.result_attachment_pdf){
            mimetype = 'application/pdf';
        }
        else{
            mimetype = event.result_mimetype;
        }
        var action = "";
        if (event.type == 'validation') {
            action = "validé(e)"
        } else if (event.type == 'signature') {
            action = "signé(e)"
        }
        if (event.type == 'creation') {
            action = "élaboré(e)"
        }
        attachmentName = attachmentName + " " + action + " par " + event.user_id[1];

        const attachmentInfo = {
            id: attachment_id,
            filename: attachment_filename,
            name: attachmentName,
            mimetype: mimetype,
        }
        const modelKey = {
            id: this.props.event.id,
            model: this.props.event.model           
        }

        let attachmentFile = this.getAttachmentFile(attachmentInfo, modelKey)
        if (!attachmentFile) {
            return 
        }
        this.fileViewer.open(attachmentFile)

    }
    previewSource() {
        var event = this.eventState.data;
        if(event.source_previewable == false){
            return
        }
        var attachment;
        var mimetype;
        var attachmentName = this.props.group.group[1];
        if (!attachment){
            attachment = event.source_attachment_pdf;
        }
        if (!attachment){
            attachment = event.source_attachment;
        }
        if (event.source_attachment_pdf){
            mimetype = 'application/pdf';
        }
        else{
            mimetype = event.source_mimetype;
        }
        var action = "";
        if (event.type == 'validation') {
            action = "validation";
        } else if (event.type == 'signature') {
            action = "signature";
        }
        attachmentName = attachmentName + ' soumise(e) à ' + action;
        
        const attachmentInfo = {
            id: attachment[0],
            filename: attachment[1],
            name: attachmentName,
            mimetype: mimetype,
        }
        const modelKey = {
            id: this.props.event.id,
            model: this.props.event.model           
        }

        let attachmentFile = this.getAttachmentFile(attachmentInfo, modelKey)
        if (!attachmentFile) {
            return 
        }
        this.fileViewer.open(attachmentFile)
    }

    getAttachmentFile(attachmentInfo, modelKey){
        if (!attachmentInfo || !modelKey) {
            return attachmentFile
        }
        let thread = this.store.Thread.get(modelKey)
        let attachmentFile = false;
        if (thread) {
            for (let current_attachment of thread.attachments){
                if (current_attachment.id == attachmentInfo.id) {
                    attachmentFile = current_attachment
                    break;
                }
            }
            if (!attachmentFile) {
                thread.attachments = [...thread.attachments, attachmentInfo]
                attachmentFile = thread.attachments[thread.attachments.length-1]             
            }
        }else{
            thread = this.store.Thread.insert({
                attachments: [attachmentInfo],
                id: this.props.event.id,
                model: this.props.event.model
            });
            attachmentFile = thread.attachments[0] }
        return attachmentFile

    }

    onResultActionsEnter(){
        this.actionHover.isResultHovered = true;
    }
    onResultActionsLeave(){
        this.actionHover.isResultHovered = false;
    }
    onSourceActionsEnter(){
        this.actionHover.isSourceHovered = true;
    }
    onSourceActionsLeave(){
        this.actionHover.isSourceHovered = false;
    }
    _build_state(event){
        if(event.create_date){
            event.create_date_day =  new DateTime(event.create_date).toLocaleString(DateTime.DATE_MED);
        }
        else{
            event.create_date_day = false;
        }
        event.name = '';
        if(event.step_id != false){
            event.name = event.step_id[1]
        }
        var date_day = '';
        if(event.date != false){
            date_day =  new DateTime(event.date).toLocaleString(DateTime.DATE_MED);
        }
        event.date_day = date_day;
        return event;
    }
}
Event.template = "customisable_workflow_report.EventWidget";