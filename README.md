# bnptools_xyl
bnp_gui is used in bionanoprobe beamline for data collection, original developed by Grace Luo. I worked to resolve some issues and improve the gui:
1) For XRF tomography data collection: the data collection stops when k-mean cluster segmentation did not work.
   I changed to save coarse images, histogram and fine images to the user folder. I also saved the sample xyz position as an csv file for users to check position later. I also added filters in k-mean cluster segmentation. 
2) I added user folder selection option instead of manually typing and creating user folders (flyXRF, mda etc.).
3) I added XANES data collection workflow
4) I added function to show ptychography image in the GUI, so users can select regions in ptychography image
