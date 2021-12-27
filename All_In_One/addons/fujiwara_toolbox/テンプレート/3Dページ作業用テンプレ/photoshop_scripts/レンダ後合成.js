/*
����
�t�H���_
�t�H���_��LayerSet
Document.layerSets[0].artLayers....
				    [0].layerSets

�E���C���[����ւ���Ƃ��̏u�Ԃ��猳�̔z��ԍ��ŃA�N�Z�X�ł��Ȃ����璍��
�EJS�͖������Ȃ��ƃ��[�J���ϐ��ɂȂ�Ȃ��I�N�\�d�l�B


*/

/*

	���t�H���_���̉摜�����W�E���񂷂�B
	../koma/���̏��𗘗p���ăR�}�}�X�N��؂�B�i�R�}����.jsx�ɂĐ����j
	forward�����O�̒��ɂ���ꍇ��ԏ�̂ЂƂ������G�̉��ɂ����Ă���B
*/



//�J���Ă�h�L�������g�����s
var repeat = documents.length
for (var d = 0; d < repeat; d++) {
    if (activeDocument.name != "�����_�ǂݍ���.psd") {
        continue
    }

	exec();
	//�ۑ����ĕ���
	activeDocument.save();
	activeDocument.close(SaveOptions.SAVECHANGES);
}




function exec(){
	//���t���b�V������
	//����
	var idFltI = charIDToTypeID( "FltI" );
	executeAction( idFltI, undefined, DialogModes.NO );
	
	layers = activeDocument.artLayers;
	//���C���[1�̍쐬
	layers.add();
	
	//���C���[�̏���
	for(var n = 0; n < layers.length; n++){
		layer = layers[n];
		if(layer.name != "���C���[ 1"){
			layer.remove();
			n--;
		}
	}
	
	
	
	
	//�܂����݂̃h�L�������g�̖��O�m��
	var basedoc = activeDocument;
	
	if(basedoc){
		//�\�����A�t�B���^�A�}���`�̗L���@->�t�@�C���p�X���z��ł�����B
		//openPath = new File(activeDocument.path);
		//filename = openPath.openDlg("�}������摜�̑I��","*.png",true);
		openPath = new Folder(activeDocument.path);
		filename = openPath.getFiles("*.png");
		
		//�t�@�C�����\�[�g
		//filename = filename.sort().reverse();
		filename = filename.sort();
		
		//�t�@�C���̓ǂݍ���
		if (filename.length != 0) {
			//�p�X�����񂪂Ȃ��Ȃ�܂Ń��[�v
			for(i = 0; i < 256; i++){
				//����̃t�@�C�����X�L�b�v
				if(String(filename[i]).match("untitled") != null){continue;}
				if(String(filename[i]).match("page_") != null){continue;}
				
				img = loadimg(filename[i])
				if(img == false){break;}
			}
		}
	}
	
	
	//���C���[�̏���
	layers = activeDocument.artLayers;
	//�ꖇ�����Ȃ�����������Ȃ��̂Ŕ�΂�
	if(layers.length != 1){
		for(var n = 0; n < layers.length; n++){
			layer = layers[n];
			if(layer.name == "���C���[ 1"){layer.remove();}
		}
	}
	
	/*
		�t�H���_��I�������png���ꖇ�J���āA
		�����ɂǂ�ǂ�t�H���_���̃t�@�C����ǂݍ���
		�t�H���_�\������������A_all����̃t�H���_�ɂ܂Ƃ߂Ĕ�\���ɂ����肵��
		unite.psd�݂����Ȗ��O�ŕۑ�����
		
		
		���Ă悭�悭�l�����炱���܂ł͊����̂ł���Ă������珈�������ق��������̂ł�
		
	*/
	
	layers = activeDocument.artLayers;
	folders = new Array();
	//�t�H���_�쐬
	//makefolder("");
//	�L����3D = makefolder(activeDocument,"�L����3D");

	//�t�H���_�쐬
	for(var n = 0; n < layers.length;n++){
		var layer = layers[n];
		//���O�̕���
		//num = layer.name.split("_")[0];
		numbase = layer.name.split("_");
		num = numbase[0];
		if(numbase[1] != null){
			num += "_"+numbase[1];
		}

		var found = false;
		for(var i = 0; i < folders.length;i++){
			folder = folders[i];
			if(folder.name == num){
				found = true;
				break;
			}
		}
		if(!found){
			//���X�g�ɂȂ������̂Ńt�H���_�[���쐬����
			folderObj = activeDocument.layerSets.add();
			folderObj.name = num;
			folders.push(folderObj);
		}
	}
	//��ԏ����Z�ɂ���
	//��Z();

	//���n�̑Ώۂ��ǂ�ɂ��邩
	var ���n�^�[�Q�b�g = "_solid"
	for(var n = 0; n < layers.length;n++){
		layer = layers[n];
		var tmptargetname = ""
		tmptargetname = "_solid"
		if(layer.name.match(tmptargetname) != null){
			���n�^�[�Q�b�g = tmptargetname;
			break;
		}
		tmptargetname = "_flatcolor"
		if(layer.name.match(tmptargetname) != null){
			���n�^�[�Q�b�g = tmptargetname;
			break;
		}
		tmptargetname = "_shadow"
		if(layer.name.match(tmptargetname) != null){
			���n�^�[�Q�b�g = tmptargetname;
			break;
		}
	}

	//���C���[�̈ړ�
	for(var n = 0; n < layers.length;n++){
		layer = layers[n];
		numbase = layer.name.split("_");
		num = numbase[0];
		if(numbase[1] != null){
			num += "_"+numbase[1];
		}

		for(var i = 0; i < folders.length;i++){
			folder = folders[i];
			if(folder.name == num){
				if(layer.name.match(���n�^�[�Q�b�g ) != null){
					dup = layer.duplicate();
					activeDocument.activeLayer = dup;
					dup.move(folder,ElementPlacement.PLACEATEND);
					//���n
					dup = layer;
					dup.name += "���n"
					activeDocument.activeLayer = dup;
					���x���␳��();
					�}�[�W();
					dup.move(folder,ElementPlacement.PLACEATEND);
					n--;
				}else{
					layer.move(folder,ElementPlacement.PLACEATBEGINNING);
					n--;
				}
				if(layer.name.match("_materials") != null){
					layer.visible = false;
				}

				break;
			}
		}
	}


	/*
		�ĂуR�}�̈ړ�
		
		�R�}���ƂɃt�H���_�����B
		
	*/
	//���t�H���_�̉��
	basefolderslist = new Array()
	basenumlist = new Array()
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		 folder = activeDocument.layerSets[n];
		 
		 //���O����R�}�����擾����
		 num = folder.name.split("_")[0].match(/\d+/i)
		 if(num != null){
			 basenumlist.push(num)
			 basefolderslist.push(folder)
		 }
	}
	//�d���폜
	numlist = new Array()
	for(var n = 0; n < basenumlist.length; n++){
		num = basenumlist[n];
		
		var found = false
		for(var i = 0; i < numlist.length; i++){
			if(""+num == ""+numlist[i]){
				found = true
				break
			}
		}
		if(found == false){
			numlist.push(num)
		}
	}
	
	
//	alert(numlist.join())
	numlist.reverse()
	for(var n = 0; n < numlist.length; n++){
		num = numlist[n];
		//�R�}�t�H���_�쐬
		makefolder(activeDocument,"�R�}"+num)
	}
	
	
	
	
//	for(var n = 0; n < basefolderslist.length; n++){
//		folder = basefolderslist[n];
	targetnames = new Array
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		folder = activeDocument.layerSets[n];
		if(folder.name.match(/�R�}/)!=null){continue}
		if(folder == undefined){continue}
		if(folder == null){continue}
//		alert(folder.name)
		 num = folder.name.split("_")[0].match(/\d+/i)
//		alert(folder.name+":"+num)
		 if(num != null){
		 	targetnames.push(folder.name)
//			komafolder = getfolderobj("�R�}"+num)
////			alert(komafolder.typename)
//			if(komafolder != null){
				
//				moveLayerSet(folder,komafolder)
//			 	alert(folder.name + "/" + num + ":" + komafolder.name)
//				activeDocument.activeLayer = folder;
//				folder.moveAfter(komafolder)
//				activeDocument.activeLayer = folder;
//				�O��()

//				folder.move(komafolder, ElementPlacement.INSIDE)

//				moveLayerSet( folder, komafolder) 
//				folder.moveToEnd(komafolder)
//activeDocument.layers[0].moveToEnd(komafolder)
//				layer = komafolder.artLayers.add()
//				activeDocument.activeLayer = komafolder;
//				folder.move(komafolder, ElementPlacement.INSIDE)
//				folder.moveAfter(layer)
//				folder.move(komafolder.layerSets, ElementPlacement.INSIDE)
//				activeDocument.layerSets[2].move(activeDocument.layerSets[0],ElementPlacement.PLACEATEND)
//				folder.moveToEnd(komafolder)
//			}
		 }
	}
//	alert(targetnames.join())
	for(var n = 0; n < targetnames.length; n++){
		folder = getfolderobj(targetnames[n]);
		num = folder.name.split("_")[0].match(/\d+/i)
		if(num != null){
			komafolder = getfolderobj("�R�}"+num)
			if(komafolder != null){
//				alert(folder.name+":"+komafolder.name)
				movebyname(folder,komafolder)
			}
		}
	}

	
	
//	komalist = new Array()
//	for(var num in numlist){
//		komalist.push(makefolder(activeDocument,"�R�}"+num))
//	}
//	
	//�t�H���_�̈ړ�
	
	
	
	�x�^�h��("�w�i")
	���X�^���C�Y()
	�}�X�N�K�p()
	�Ŕw��()
	�Ŕw��()
	�Ŕw��()
	�Ŕw��()
	
	//�w�i���[�h
	docpath =new String( activeDocument.path)
	parent_dir = docpath.replace(new String(activeDocument.path.name),"")
	if(loadimg(parent_dir+"background.png") != false){
		�őO��()
		�őO��()
		��Z()
	}
	
//	�s�����x(30)
	komamask()
	
	/*
		��O����
		�t�H���_����forward���ē����Ă����ԏ�ɂ����Ă���ׂ��B
	*/
	for(var i = 0; i < activeDocument.layerSets.length; i++){
		var layerSets = activeDocument.layerSets[i];
		for(var j = 0; j < layerSets.layerSets.length; j++){
			var subSets = layerSets.layerSets[j];
			if(subSets.name.match("forward") != null){
				activeDocument.activeLayer = subSets
				�őO��()
				�őO��()
				�őO��()
				�őO��()
				�őO��()
				�őO��()
				�w��()
			}
		}
	}
	
	
	
	
	/*��t�J�X�^������*/
	
	��t�J�X�^������()
	
	
	
}

function komamask(){
	/*
	�R�}�Ƀ}�X�N�����鏈��
	*/
	komafolder = new Folder(activeDocument.path+"/../koma/")
	if(komafolder.exists){
		//�R�}�t�H���_��������
		for(var n = 0; n < activeDocument.layerSets.length; n++){
			 layerset = activeDocument.layerSets[n];
			 if(layerset.name.match("�R�}") != null){
			 	var komafilepath = komafolder.absoluteURI + "/" + layerset.name.replace("�R�}", "") + ".png"
			 	hideall()
			 	loadimg(komafilepath)
			 	�F���()
			 	activeDocument.activeLayer.remove()
			 	showall()
			 	activeDocument.activeLayer = layerset
			 	�}�X�N�쐻()
			 	�I������()
			 }
		}
	}
}
































function makefolder(folder,name){
	folderObj = folder.layerSets.add();
	folderObj.name = name;
	folders.push(folderObj);
	return folderObj;
}

function getfolderobj(name){
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		var folder = activeDocument.layerSets[n];
		if(folder.name == name){return folder}
	}

//	for(var n = 0; n < folders.length; n++){
//		folder = folders[n];
//		if(folder.name.match(name) != null){
//			return folder;
//		}
//	}

	return null;
}


function ���x���␳��(){
			//���x���␳�@�^�����Ɂi���n�p�j
			// =======================================================
			var idMk = charIDToTypeID( "Mk  " );
			    var desc45 = new ActionDescriptor();
			    var idnull = charIDToTypeID( "null" );
			        var ref40 = new ActionReference();
			        var idAdjL = charIDToTypeID( "AdjL" );
			        ref40.putClass( idAdjL );
			    desc45.putReference( idnull, ref40 );
			    var idUsng = charIDToTypeID( "Usng" );
			        var desc46 = new ActionDescriptor();
			        var idType = charIDToTypeID( "Type" );
			            var desc47 = new ActionDescriptor();
			            var idpresetKind = stringIDToTypeID( "presetKind" );
			            var idpresetKindType = stringIDToTypeID( "presetKindType" );
			            var idpresetKindDefault = stringIDToTypeID( "presetKindDefault" );
			            desc47.putEnumerated( idpresetKind, idpresetKindType, idpresetKindDefault );
			        var idLvls = charIDToTypeID( "Lvls" );
			        desc46.putObject( idType, idLvls, desc47 );
			    var idAdjL = charIDToTypeID( "AdjL" );
			    desc45.putObject( idUsng, idAdjL, desc46 );
			executeAction( idMk, desc45, DialogModes.NO );
			
			// =======================================================
			var idsetd = charIDToTypeID( "setd" );
			    var desc48 = new ActionDescriptor();
			    var idnull = charIDToTypeID( "null" );
			        var ref41 = new ActionReference();
			        var idAdjL = charIDToTypeID( "AdjL" );
			        var idOrdn = charIDToTypeID( "Ordn" );
			        var idTrgt = charIDToTypeID( "Trgt" );
			        ref41.putEnumerated( idAdjL, idOrdn, idTrgt );
			    desc48.putReference( idnull, ref41 );
			    var idT = charIDToTypeID( "T   " );
			        var desc49 = new ActionDescriptor();
			        var idpresetKind = stringIDToTypeID( "presetKind" );
			        var idpresetKindType = stringIDToTypeID( "presetKindType" );
			        var idpresetKindCustom = stringIDToTypeID( "presetKindCustom" );
			        desc49.putEnumerated( idpresetKind, idpresetKindType, idpresetKindCustom );
			        var idAdjs = charIDToTypeID( "Adjs" );
			            var list16 = new ActionList();
			                var desc50 = new ActionDescriptor();
			                var idChnl = charIDToTypeID( "Chnl" );
			                    var ref42 = new ActionReference();
			                    var idChnl = charIDToTypeID( "Chnl" );
			                    var idChnl = charIDToTypeID( "Chnl" );
			                    var idCmps = charIDToTypeID( "Cmps" );
			                    ref42.putEnumerated( idChnl, idChnl, idCmps );
			                desc50.putReference( idChnl, ref42 );
			                var idInpt = charIDToTypeID( "Inpt" );
			                    var list17 = new ActionList();
			                    list17.putInteger( 253 );
			                    list17.putInteger( 255 );
			                desc50.putList( idInpt, list17 );
			                var idOtpt = charIDToTypeID( "Otpt" );
			                    var list18 = new ActionList();
			                    list18.putInteger( 255 );
			                    list18.putInteger( 255 );
			                desc50.putList( idOtpt, list18 );
			            var idLvlA = charIDToTypeID( "LvlA" );
			            list16.putObject( idLvlA, desc50 );
			        desc49.putList( idAdjs, list16 );
			    var idLvls = charIDToTypeID( "Lvls" );
			    desc48.putObject( idT, idLvls, desc49 );
			executeAction( idsetd, desc48, DialogModes.NO );

}

function �}�[�W(){
			//�}�[�W
			// =======================================================
			var idMrgtwo = charIDToTypeID( "Mrg2" );
			    var desc31 = new ActionDescriptor();
			executeAction( idMrgtwo, desc31, DialogModes.NO );

}

function ��l��(level){
	var idMk = charIDToTypeID( "Mk  " );
	    var desc81 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref71 = new ActionReference();
	        var idAdjL = charIDToTypeID( "AdjL" );
	        ref71.putClass( idAdjL );
	    desc81.putReference( idnull, ref71 );
	    var idUsng = charIDToTypeID( "Usng" );
	        var desc82 = new ActionDescriptor();
	        var idType = charIDToTypeID( "Type" );
	            var desc83 = new ActionDescriptor();
	            var idLvl = charIDToTypeID( "Lvl " );
	            desc83.putInteger( idLvl, level );
	        var idThrs = charIDToTypeID( "Thrs" );
	        desc82.putObject( idType, idThrs, desc83 );
	    var idAdjL = charIDToTypeID( "AdjL" );
	    desc81.putObject( idUsng, idAdjL, desc82 );
	executeAction( idMk, desc81, DialogModes.NO );
}

function �N���b�s���O�}�X�N(){
	var idGrpL = charIDToTypeID( "GrpL" );
	    var desc84 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref72 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idTrgt = charIDToTypeID( "Trgt" );
	        ref72.putEnumerated( idLyr, idOrdn, idTrgt );
	    desc84.putReference( idnull, ref72 );
	executeAction( idGrpL, desc84, DialogModes.NO );
}


//https://forums.adobe.com/thread/925247
function moveLayerSet( fromLayer, toLayer ){// layerSet objects  
    var desc = new ActionDescriptor();  
        var sourceRef = new ActionReference();  
        sourceRef.putName( charIDToTypeID( "Lyr " ), fromLayer.name );  
    desc.putReference( charIDToTypeID( "null" ), sourceRef );  
            var indexRef = new ActionReference();  
            indexRef.putName( charIDToTypeID("Lyr "), toLayer.name );  
            var layerIndex = executeActionGet(indexRef).getInteger(stringIDToTypeID('itemIndex'));  
        var destinationRef = new ActionReference();  
        destinationRef.putIndex( charIDToTypeID( "Lyr " ), layerIndex-1 );  
    desc.putReference( charIDToTypeID( "T   " ), destinationRef );  
    desc.putBoolean( charIDToTypeID( "Adjs" ), false );  
    desc.putInteger( charIDToTypeID( "Vrsn" ), 5 );  
    executeAction( charIDToTypeID( "move" ), desc, DialogModes.NO );  
}  


function ��Z(){
	// =======================================================
	var idsetd = charIDToTypeID( "setd" );
	    var desc2 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref1 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idTrgt = charIDToTypeID( "Trgt" );
	        ref1.putEnumerated( idLyr, idOrdn, idTrgt );
	    desc2.putReference( idnull, ref1 );
	    var idT = charIDToTypeID( "T   " );
	        var desc3 = new ActionDescriptor();
	        var idMd = charIDToTypeID( "Md  " );
	        var idBlnM = charIDToTypeID( "BlnM" );
	        var idMltp = charIDToTypeID( "Mltp" );
	        desc3.putEnumerated( idMd, idBlnM, idMltp );
	    var idLyr = charIDToTypeID( "Lyr " );
	    desc2.putObject( idT, idLyr, desc3 );
	executeAction( idsetd, desc2, DialogModes.NO );
}

function ���X�^���C�Y(){
// =======================================================
var idrasterizeLayer = stringIDToTypeID( "rasterizeLayer" );
    var desc17 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
        var ref6 = new ActionReference();
        var idLyr = charIDToTypeID( "Lyr " );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idTrgt = charIDToTypeID( "Trgt" );
        ref6.putEnumerated( idLyr, idOrdn, idTrgt );
    desc17.putReference( idnull, ref6 );
executeAction( idrasterizeLayer, desc17, DialogModes.NO );
}

function �}�X�N�K�p(){
	// =======================================================
	var idDlt = charIDToTypeID( "Dlt " );
	    var desc18 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref7 = new ActionReference();
	        var idChnl = charIDToTypeID( "Chnl" );
	        var idChnl = charIDToTypeID( "Chnl" );
	        var idMsk = charIDToTypeID( "Msk " );
	        ref7.putEnumerated( idChnl, idChnl, idMsk );
	    desc18.putReference( idnull, ref7 );
	    var idAply = charIDToTypeID( "Aply" );
	    desc18.putBoolean( idAply, true );
	executeAction( idDlt, desc18, DialogModes.NO );
}

function �x�^�h��(layername){
	// =======================================================
	var idMk = charIDToTypeID( "Mk  " );
	    var desc6 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref2 = new ActionReference();
	        var idcontentLayer = stringIDToTypeID( "contentLayer" );
	        ref2.putClass( idcontentLayer );
	    desc6.putReference( idnull, ref2 );
	    var idUsng = charIDToTypeID( "Usng" );
	        var desc7 = new ActionDescriptor();
	        var idNm = charIDToTypeID( "Nm  " );
	        desc7.putString( idNm, layername );
	        var idType = charIDToTypeID( "Type" );
	            var desc8 = new ActionDescriptor();
	            var idClr = charIDToTypeID( "Clr " );
	                var desc9 = new ActionDescriptor();
	                var idRd = charIDToTypeID( "Rd  " );
	                desc9.putDouble( idRd, 255.000000 );
	                var idGrn = charIDToTypeID( "Grn " );
	                desc9.putDouble( idGrn, 255.000000 );
	                var idBl = charIDToTypeID( "Bl  " );
	                desc9.putDouble( idBl, 255.000000 );
	            var idRGBC = charIDToTypeID( "RGBC" );
	            desc8.putObject( idClr, idRGBC, desc9 );
	        var idsolidColorLayer = stringIDToTypeID( "solidColorLayer" );
	        desc7.putObject( idType, idsolidColorLayer, desc8 );
	    var idcontentLayer = stringIDToTypeID( "contentLayer" );
	    desc6.putObject( idUsng, idcontentLayer, desc7 );
	executeAction( idMk, desc6, DialogModes.NO );

	return activeDocument.activeLayer;

}


function �s�����x(percentage){
// =======================================================
var idsetd = charIDToTypeID( "setd" );
    var desc20 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
        var ref19 = new ActionReference();
        var idLyr = charIDToTypeID( "Lyr " );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idTrgt = charIDToTypeID( "Trgt" );
        ref19.putEnumerated( idLyr, idOrdn, idTrgt );
    desc20.putReference( idnull, ref19 );
    var idT = charIDToTypeID( "T   " );
        var desc21 = new ActionDescriptor();
        var idOpct = charIDToTypeID( "Opct" );
        var idPrc = charIDToTypeID( "#Prc" );
        desc21.putUnitDouble( idOpct, idPrc, percentage);
    var idLyr = charIDToTypeID( "Lyr " );
    desc20.putObject( idT, idLyr, desc21 );
executeAction( idsetd, desc20, DialogModes.NO );
}
/*
�t�@�C�������C���[�ɓǂݍ���
*/

function loadimg(filename){
	var basedoc = activeDocument
	fileObj = new File(filename);
	if(filename == null){return false;}
	if(fileObj.exists == false){return false}
	//�p�X���J���B
	app.open(fileObj);
	
	//��̃��C���[�̓X�L�b�v
	if(
		(activeDocument.activeLayer.bounds[0].value == 0)&&
		(activeDocument.activeLayer.bounds[1].value == 0)&&
		(activeDocument.activeLayer.bounds[2].value == 0)&&
		(activeDocument.activeLayer.bounds[3].value == 0)
	){
		activeDocument.close(SaveOptions.DONOTSAVECHANGES);
		return true;
	}
	
	//�T�C�Y�擾
	targetwidth = app.activeDocument.width
	targetheight = app.activeDocument.height

	layername = activeDocument.name;
	//activeDocument.artLayers[0].name = activeDocument.name;
	
	//����
	activeDocument.activeLayer.duplicate(basedoc)
	//����
	// =======================================================
	activeDocument.close(SaveOptions.DONOTSAVECHANGES);
	activeDocument.activeLayer.name = layername;

	//�T�C�Y��������獇�킹��
	if((activeDocument.width != targetwidth)||(activeDocument.height != targetheight)){
		preferences.rulerUnits = Units.PIXELS;
		activeDocument.resizeCanvas(targetwidth,targetheight,AnchorPosition.MIDDLECENTER);
	}

	//���C���[��Ԃ��Ό㏈���y�H
	return activeDocument.activeLayer;
}


function �Ŕw��(){
	// =======================================================
	var idmove = charIDToTypeID( "move" );
	    var desc11 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref7 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idTrgt = charIDToTypeID( "Trgt" );
	        ref7.putEnumerated( idLyr, idOrdn, idTrgt );
	    desc11.putReference( idnull, ref7 );
	    var idT = charIDToTypeID( "T   " );
	        var ref8 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idBack = charIDToTypeID( "Back" );
	        ref8.putEnumerated( idLyr, idOrdn, idBack );
	    desc11.putReference( idT, ref8 );
	executeAction( idmove, desc11, DialogModes.NO );
}

function �őO��(){
	// =======================================================
	var idmove = charIDToTypeID( "move" );
	    var desc10 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref5 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idTrgt = charIDToTypeID( "Trgt" );
	        ref5.putEnumerated( idLyr, idOrdn, idTrgt );
	    desc10.putReference( idnull, ref5 );
	    var idT = charIDToTypeID( "T   " );
	        var ref6 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idFrnt = charIDToTypeID( "Frnt" );
	        ref6.putEnumerated( idLyr, idOrdn, idFrnt );
	    desc10.putReference( idT, ref6 );
	executeAction( idmove, desc10, DialogModes.NO );
	

}

function �O��(){
// =======================================================
var idmove = charIDToTypeID( "move" );
    var desc12 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
        var ref12 = new ActionReference();
        var idLyr = charIDToTypeID( "Lyr " );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idTrgt = charIDToTypeID( "Trgt" );
        ref12.putEnumerated( idLyr, idOrdn, idTrgt );
    desc12.putReference( idnull, ref12 );
    var idT = charIDToTypeID( "T   " );
        var ref13 = new ActionReference();
        var idLyr = charIDToTypeID( "Lyr " );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idNxt = charIDToTypeID( "Nxt " );
        ref13.putEnumerated( idLyr, idOrdn, idNxt );
    desc12.putReference( idT, ref13 );
executeAction( idmove, desc12, DialogModes.NO );

}


function �w��(){
	// =======================================================
	var idmove = charIDToTypeID( "move" );
	    var desc8 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref4 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idTrgt = charIDToTypeID( "Trgt" );
	        ref4.putEnumerated( idLyr, idOrdn, idTrgt );
	    desc8.putReference( idnull, ref4 );
	    var idT = charIDToTypeID( "T   " );
	        var ref5 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idPrvs = charIDToTypeID( "Prvs" );
	        ref5.putEnumerated( idLyr, idOrdn, idPrvs );
	    desc8.putReference( idT, ref5 );
	executeAction( idmove, desc8, DialogModes.NO );

}


////���C���[id���烌�C���[�I�u�W�F�N�g���擾����
//function lid(layerid){}

function movebyname(fromobj, toobj){
	fromname = fromobj.name
	toname = toobj.name
//	getfolderobj(fromname).move(getfolderobj(toname), ElementPlacement.INSIDE)
	getfolderobj(fromname).moveAfter(getfolderobj(toname))
	activeDocument.activeLayer = getfolderobj(fromname)
	�O��()
}

function setActiveLayer(layername){
	layer = activeDocument.artLayers.getByName(layername)
	if(layer != undefined){
		activeDocument.activeLayer = layer
	}else{}
}


function �F���(){
	// =======================================================
	var idClrR = charIDToTypeID( "ClrR" );
	    var desc15 = new ActionDescriptor();
	    var idFzns = charIDToTypeID( "Fzns" );
	    desc15.putInteger( idFzns, 200 );
	    var idMnm = charIDToTypeID( "Mnm " );
	        var desc16 = new ActionDescriptor();
	        var idLmnc = charIDToTypeID( "Lmnc" );
	        desc16.putDouble( idLmnc, 54.290000 );
	        var idA = charIDToTypeID( "A   " );
	        desc16.putDouble( idA, 80.800000 );
	        var idB = charIDToTypeID( "B   " );
	        desc16.putDouble( idB, 69.900000 );
	    var idLbCl = charIDToTypeID( "LbCl" );
	    desc15.putObject( idMnm, idLbCl, desc16 );
	    var idMxm = charIDToTypeID( "Mxm " );
	        var desc17 = new ActionDescriptor();
	        var idLmnc = charIDToTypeID( "Lmnc" );
	        desc17.putDouble( idLmnc, 54.290000 );
	        var idA = charIDToTypeID( "A   " );
	        desc17.putDouble( idA, 80.800000 );
	        var idB = charIDToTypeID( "B   " );
	        desc17.putDouble( idB, 69.900000 );
	    var idLbCl = charIDToTypeID( "LbCl" );
	    desc15.putObject( idMxm, idLbCl, desc17 );
	    var idcolorModel = stringIDToTypeID( "colorModel" );
	    desc15.putInteger( idcolorModel, 0 );
	executeAction( idClrR, desc15, DialogModes.NO );

}

function �}�X�N�쐻(){
	// =======================================================
	var idMk = charIDToTypeID( "Mk  " );
	    var desc24 = new ActionDescriptor();
	    var idNw = charIDToTypeID( "Nw  " );
	    var idChnl = charIDToTypeID( "Chnl" );
	    desc24.putClass( idNw, idChnl );
	    var idAt = charIDToTypeID( "At  " );
	        var ref10 = new ActionReference();
	        var idChnl = charIDToTypeID( "Chnl" );
	        var idChnl = charIDToTypeID( "Chnl" );
	        var idMsk = charIDToTypeID( "Msk " );
	        ref10.putEnumerated( idChnl, idChnl, idMsk );
	    desc24.putReference( idAt, ref10 );
	    var idUsng = charIDToTypeID( "Usng" );
	    var idUsrM = charIDToTypeID( "UsrM" );
	    var idRvlS = charIDToTypeID( "RvlS" );
	    desc24.putEnumerated( idUsng, idUsrM, idRvlS );
	executeAction( idMk, desc24, DialogModes.NO );
	

}

function �I������(){
	// =======================================================
	var idsetd = charIDToTypeID( "setd" );
	    var desc26 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref12 = new ActionReference();
	        var idChnl = charIDToTypeID( "Chnl" );
	        var idfsel = charIDToTypeID( "fsel" );
	        ref12.putProperty( idChnl, idfsel );
	    desc26.putReference( idnull, ref12 );
	    var idT = charIDToTypeID( "T   " );
	    var idOrdn = charIDToTypeID( "Ordn" );
	    var idNone = charIDToTypeID( "None" );
	    desc26.putEnumerated( idT, idOrdn, idNone );
	executeAction( idsetd, desc26, DialogModes.NO );


}



function showall(){
 	//���̃��C���[�̕\��
	for(var i = 0; i < activeDocument.layers.length; i++){
		var layer = activeDocument.layers[i];
		layer.visible = true
	}
	for(var i = 0; i < activeDocument.layerSets.length; i++){
		var layerset = activeDocument.layerSets[i];
		layerset.visible = true
	}
}

function hideall(){
	 	//���̃��C���[�̔�\��
	for(var i = 0; i < activeDocument.layers.length; i++){
		var layer = activeDocument.layers[i];
		layer.visible = false
	}
	for(var i = 0; i < activeDocument.layerSets.length; i++){
		var layerset = activeDocument.layerSets[i];
		layerset.visible = false
	}

}






function ��t�J�X�^������(){

/*	����Ȃ��Ȃ��������B
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		var lset = activeDocument.layerSets[n];
		���΂Ńt�H���_�}�X�N(lset)
	}
*/

}

function ���΂Ńt�H���_�}�X�N(layerset){
	for(var n = 0; n < layerset.layerSets.length; n++){
		 var tmplset = layerset.layerSets[n];
		 ���΂Ńt�H���_�}�X�N(tmplset)
	}
	
	for(var m = 0; m < layerset.layers.length; m++){
		 layer = layerset.layers[m];
		 if(layer.name.match(/flatcolor/i) != null){
		 	
		 	activeDocument.activeLayer = layer
		 	���C���[��S�Ĕ�\��()
		 	layer.visible = true
		 	���΂�I��()
		 	//�I��͈͂�����΁B
		 	//http://www.openspc2.org/book/PhotoshopCC/easy/selection/012/index.html
		 	if(checkSelection()){
		 		�I��͈͂̊g��()
		 		//�e�t�H���_�Ƀ}�X�N������
		 		if(layer.parent != null){
		 			activeDocument.activeLayer = layer.parent
		 			�I�𔽓]()
		 			�}�X�N�쐻()
		 		}
		 	}
		}
	}
	
	���C���[��S�ĕ\��()
}

function �I��͈͂̊g��(){
    // ==============================================   =========
    var idExpn = charIDToTypeID( "Expn" );
        var desc34 = new ActionDescriptor();
        var idBy = charIDToTypeID( "By  " );
        var idPxl = charIDToTypeID( "#Pxl" );
        desc34.putUnitDouble( idBy, idPxl, 2.000000 );
        var idselectionModifyEffectAtCanvasBounds = stringIDToTypeID( "selectionModif   yEffectAtCanvasBounds" );
        desc34.putBoolean( idselectionModifyEffectAtCanvasBounds, false );
    executeAction( idExpn, desc34, DialogModes.NO );
    

}

function ���΂�I��(){
    // ==============================================   =========
    var idClrR = charIDToTypeID( "ClrR" );
        var desc42 = new ActionDescriptor();
        var idFzns = charIDToTypeID( "Fzns" );
        desc42.putInteger( idFzns, 24 );
        var idMnm = charIDToTypeID( "Mnm " );
            var desc43 = new ActionDescriptor();
            var idLmnc = charIDToTypeID( "Lmnc" );
            desc43.putDouble( idLmnc, 87.820000 );
            var idA = charIDToTypeID( "A   " );
            desc43.putDouble( idA, -79.270000 );
            var idB = charIDToTypeID( "B   " );
            desc43.putDouble( idB, 81.000000 );
        var idLbCl = charIDToTypeID( "LbCl" );
        desc42.putObject( idMnm, idLbCl, desc43 );
        var idMxm = charIDToTypeID( "Mxm " );
            var desc44 = new ActionDescriptor();
            var idLmnc = charIDToTypeID( "Lmnc" );
            desc44.putDouble( idLmnc, 87.820000 );
            var idA = charIDToTypeID( "A   " );
            desc44.putDouble( idA, -79.270000 );
            var idB = charIDToTypeID( "B   " );
            desc44.putDouble( idB, 81.000000 );
        var idLbCl = charIDToTypeID( "LbCl" );
        desc42.putObject( idMxm, idLbCl, desc44 );
        var idcolorModel = stringIDToTypeID( "colorModel" );
        desc42.putInteger( idcolorModel, 0 );
    executeAction( idClrR, desc42, DialogModes.NO );
    
}


function checkSelection()
{
	var flag = true;
	try {
		activeDocument.selection.translate(0,0);
	}catch(e){
		flag = false;
	}
	return flag;
}

function �I�𔽓](){
	var idInvs = charIDToTypeID( "Invs" );
	executeAction( idInvs, undefined, DialogModes.NO );
}


function �q���\��(layerset){
	for(var n = 0; n < layerset.layerSets.length; n++){
		 var tmplset = layerset.layerSets[n];
		 �q���\��(tmplset)
	}
	for(var i = 0; i < layerset.artLayers.length; i++){
		 var layer = layerset.artLayers[i];
		 layer.visible = false
	}
}
function ���C���[��S�Ĕ�\��(){
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		 layerset = activeDocument.layerSets[n];
		 �q���\��(layerset)
	}
}


function �q��\��(layerset){
	for(var n = 0; n < layerset.layerSets.length; n++){
		 var tmplset = layerset.layerSets[n];
		 �q��\��(tmplset)
	}
	for(var i = 0; i < layerset.artLayers.length; i++){
		 var layer = layerset.artLayers[i];
		 layer.visible = true
	}
}
function ���C���[��S�ĕ\��(){
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		 layerset = activeDocument.layerSets[n];
		 �q��\��(layerset)
	}
}