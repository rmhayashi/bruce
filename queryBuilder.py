def builder(query, campo):
    if query == 'idsDoc':
        return ("""SELECT  CONTA.INTEGRATION_ID CONTA,  ENDERECO.INTEGRATION_ID ENDERECO_VELHO,
                                INSTANCIA.SERIAL_NUM, PRODUTO.NAME, INSTANCIA.X_VOICE_TECHNOLOGY, INSTANCIA.X_ACCESS_TECHNOLOGY ,CONTA.x_doc_number CPF,ENDERECO.X_NETWORK_OWNER as REDE
                                FROM 
                                        SIEBEL.S_ASSET INSTANCIA,
                                        SIEBEL.S_PROD_INT PRODUTO,
                                        SIEBEL.S_ASSET_OM END_INSTANCIA,
                                        SIEBEL.S_ADDR_PER ENDERECO,
                                        SIEBEL.S_ORG_EXT CONTA
                                        
                                WHERE 1=1
                                AND END_INSTANCIA.PAR_ROW_ID = INSTANCIA.ROW_ID
                                AND PRODUTO.ROW_ID = INSTANCIA.PROD_ID
                                AND END_INSTANCIA.FROM_ADDR_ID = ENDERECO.ROW_ID
                                AND ENDERECO.X_ACCOUNT_ID = CONTA.ROW_ID
                                AND INSTANCIA.STATUS_CD = 'Ativo'
                                AND ENDERECO.INTEGRATION_ID IN ( SELECT  ENDERECO.INTEGRATION_ID FROM 
                                        SIEBEL.S_ASSET INSTANCIA,
                                        SIEBEL.S_PROD_INT PRODUTO,
                                        SIEBEL.S_ASSET_OM END_INSTANCIA,
                                        SIEBEL.S_ADDR_PER ENDERECO,
                                        SIEBEL.S_ORG_EXT CONTA
                                        
                                WHERE 1=1
                                AND END_INSTANCIA.PAR_ROW_ID = INSTANCIA.ROW_ID
                                AND PRODUTO.ROW_ID = INSTANCIA.PROD_ID
                                AND END_INSTANCIA.FROM_ADDR_ID = ENDERECO.ROW_ID
                                AND ENDERECO.X_ACCOUNT_ID = CONTA.ROW_ID
                                AND CONTA.x_doc_number = '{}'
                                AND INSTANCIA.STATUS_CD = 'Ativo');""").format(campo), "SIEBEL"
    elif query == 'ordemInst':
        return ("""select  C.INTEGRATION_ID conta, e.INTEGRATION_ID endereco, c.name,o.integration_id,o.BILL_ACCNT_ID , to_char(o.last_upd, 'DD/MM/YYYY HH24:MI:SS')  as ult  , o.status_cd, to_char(o.created, 'DD/MM/YYYY HH24:MI:SS') as created, o.x_order_type,order_id, action_cd , i.status_cd,i.created, i.last_upd  , o.x_sync_type
                                from siebel.s_order_item i,     
                                siebel.s_order o,
                                siebel.s_org_ext c,
                                SIEBEL.S_ADDR_PER e
                                where prod_id='1-5WPB'  
                                and o.row_id=i.order_id
                                and service_num = '{}'
                                and c.row_id=o.BILL_ACCNT_ID
                                AND e.X_ACCOUNT_ID = c.ROW_ID
                                order by i.created desc""").format(campo), "SIEBEL"
    elif query == 'cxAtv':
        return ("""Select *
                                FROM SIEBEL.CX_LOGGING
                                where object_id = (select row_id from siebel.s_order where integration_id = '{}}');""").format(campo), "SIEBEL"
    elif query == 'cxIns1':
        return ("""Select X_Serv_Addr_Id Id_Endereco 
                                From Siebel.S_Order_Item 
                                WHERE ROW_ID = '{}}';""").format(campo), "SIEBEL"
    elif query == 'cxIns2':
        return ("""SELECT LOGGED_MESSAGE_LONG MSG_ERRO, REQUEST_XML
                                FROM SIEBEL.CX_LOGGING CX 
                                WHERE LOG_LEVEL = 'WEB SERVICE EXCEPTION'
                                AND CREATED = (SELECT MAX(CREATED) FROM SIEBEL.CX_LOGGING WHERE OBJECT_ID = CX.OBJECT_ID
                                                And Log_Level = 'WEB SERVICE EXCEPTION')
                                And Object_Id = '{}';""").format(campo), "SIEBEL"