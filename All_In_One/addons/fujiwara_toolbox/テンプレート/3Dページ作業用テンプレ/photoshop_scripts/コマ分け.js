/*
����
�t�H���_
�t�H���_��LayerSet
Document.layerSets[0].artLayers....
				    [0].layerSets

�E���C���[����ւ���Ƃ��̏u�Ԃ��猳�̔z��ԍ��ŃA�N�Z�X�ł��Ȃ����璍��
�EJS�͖������Ȃ��ƃ��[�J���ϐ��ɂȂ�Ȃ��I�N�\�d�l�B


*/




//�J���Ă�h�L�������g�����s
//var repeat = documents.length
//for(var d = 0; d < repeat; d++){
//	exec();
//	//�ۑ����ĕ���
////	activeDocument.save();
////	activeDocument.close(SaveOptions.SAVECHANGES);
//	activeDocument.close(SaveOptions.DONOTSAVECHANGES);
//}

//��񂾂����s
exec();
activeDocument.close(SaveOptions.DONOTSAVECHANGES);

function exec(){
	/*
		background.png���t�H�g�V���ɕ��荞��ŁA�蓮�Ŋe�R�}��h��Ԃ��Ă���A�Ƃ����O��
		���C���[2
		���C���[1���e�R�}
		���C���[0���w�i
		
		�Ƃ肠����koma�t�H���_������āA���̒��Ɋe�R�}��n.png�œ����B
		�e�R�}�̑傫�����e�L�X�g�ŏ��������Ă����B
		1.txt����x,y,width,height���Ă��񂶂ŁB�����blender���œǂݍ��ށB
	*/
	activeDocument.activeLayer = activeDocument.layers[activeDocument.layers.length-1]
	
	docpath = new Folder(activeDocument.path);
	komapath = new Folder(docpath.absoluteURI+"/koma/")
	if(!komapath.exists){
		komapath.create()
	}
	
	//��ƃt�@�C�����ꉞ�ۑ����Ƃ��B
	var savepath = new File(komapath.absoluteURI + "/koma.psd")
	var saveOptions = new PhotoshopSaveOptions()
	activeDocument.saveAs(savepath,saveOptions,true)

	
	var komacount = 1;
	for(var l = activeDocument.layers.length - 2; l >= 0; l--){
		//�S�Ĕ�\��
		for(var n = 0; n < activeDocument.layers.length; n++){
			tmplayer = activeDocument.layers[n];
			tmplayer.visible = false;
		}
		layer = activeDocument.layers[l];
		layer.visible = true;
		var savepath = new File(komapath.absoluteURI + "/" + komacount + ".png")
//		var saveOptions = new PNGSaveOptions()
//		activeDocument.saveAs(savepath,saveOptions,true)
		save_png(savepath)
		
		//�I��͈͂��e�L�X�g�ɏ����o��
		var textfile = new File(komapath.absoluteURI + "/" + komacount + ".txt")
		textfile.open("w")
		�F���()
		textfile.write(new String(activeDocument.selection.bounds).replace(/[ px]/g, ""));
		textfile.close();
		�I������()


		komacount++;
	}



	

}


//�ۑ����ĕ���
//activeDocument.save();
//activeDocument.close(SaveOptions.SAVECHANGES);


























function save_png(path){
// =======================================================
var idsave = charIDToTypeID( "save" );
    var desc17 = new ActionDescriptor();
    var idAs = charIDToTypeID( "As  " );
        var desc18 = new ActionDescriptor();
        var idPGIT = charIDToTypeID( "PGIT" );
        var idPGIT = charIDToTypeID( "PGIT" );
        var idPGIN = charIDToTypeID( "PGIN" );
        desc18.putEnumerated( idPGIT, idPGIT, idPGIN );
        var idPNGf = charIDToTypeID( "PNGf" );
        var idPNGf = charIDToTypeID( "PNGf" );
        var idPGAd = charIDToTypeID( "PGAd" );
        desc18.putEnumerated( idPNGf, idPNGf, idPGAd );
        var idCmpr = charIDToTypeID( "Cmpr" );
        desc18.putInteger( idCmpr, 9 );
    var idPNGF = charIDToTypeID( "PNGF" );
    desc17.putObject( idAs, idPNGF, desc18 );
    var idIn = charIDToTypeID( "In  " );
    desc17.putPath( idIn, new File( path ) );
    var idDocI = charIDToTypeID( "DocI" );
    desc17.putInteger( idDocI, 203 );
    var idCpy = charIDToTypeID( "Cpy " );
    desc17.putBoolean( idCpy, true );
    var idsaveStage = stringIDToTypeID( "saveStage" );
    var idsaveStageType = stringIDToTypeID( "saveStageType" );
    var idsaveSucceeded = stringIDToTypeID( "saveSucceeded" );
    desc17.putEnumerated( idsaveStage, idsaveStageType, idsaveSucceeded );
executeAction( idsave, desc17, DialogModes.NO );


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

