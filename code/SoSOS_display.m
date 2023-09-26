clear variables
clc
close all
addpath('functions/');
addpath('old/');
addpath('ESB/');
addpath('SoSOS_IxI/results');

%turn right figure tick labels and legend
turn = 0; % 1 if turned, else 0

%load dimensional sufficiency-based SoSOS
dim = 0;

%%%%% load suffiency-based SoSOS %%%%%%
if dim
    filename_basis = 'sosos_data_dim_dls_basket_basic.xlsx';
    filename_ff    = 'sosos_data_dim_dls_basket_ff_LD_wb_wo_LUC.xlsx';
else
    filename_basis = 'SoSOS_data_dls_basket_basic.xlsx';
    filename_ff    = 'SoSOS_data_dls_basket_ff_LD_wb_wo_LUC.xlsx';
end

[sosos_basis]=xlsread(filename_basis);
[sosos_ff]   =xlsread(filename_ff);

[~,sectors,~]=xlsread(filename_basis, 'A2:A16');
sectors = sectors';

boundary=categorical({'CO_2', 'CO_{2,eq}(GWP100)', 'biodiversity','ozone depletion', 'P to ocean',...
                       'P to soil','N emissions', 'land use', 'cropland use' ,'blue water','energy demand'});

if ~dim
    sectors={'Chemicals','Metals', 'Energy (carrier)',...
                    'Minerals', 'Textiles', 'Agricult., animal',...
                    'Agricult., plant-b.', 'Wood', 'Water'};
end
                
               
%%%%% load grandfathering-based SoSOS (Desing et al.)
filename_gf    ='SoSOS_materialsEnergy.xlsx';
filename_gf2suf='sosos_gf2suf.xlsx';
[sosos_gf]     =xlsread(filename_gf);
[sosos_gf2suf] =xlsread(filename_gf2suf);
target_segment ='materialsEnergy';
year_A = 2011;

addpath('SoSOS_IxI/functions/')
addpath('functions/')
addpath('SoSOS_IxI/functions/new/')
% loading prepared data
load('ESB.mat');
%load('SoSOS_IxI/Labels_Sectors_all.mat');
load(['SoSOS_IxI/results/' target_segment '/S_t.mat']);
load(['SoSOS_IxI/results/' target_segment '/index_t_s.mat']);
S = S_t;
n_ESB_gf = size(ESB,1);
[n_industries, n_sector] = size(S);

%Names_Target_Sectors = Labels_Sectors_all(index_t_s);

load(['SoSOS_IxI/results/' target_segment '/q_S_direct' target_segment '_' num2str(year_A) '.mat']);
q_A_total = sum(q_S_direct,2);

load(['SoSOS_IxI/results/' target_segment '/SoSOS_S_wdc_' target_segment '_' num2str(year_A) '.mat']);
SoSOS_q_A = quantile(SoSOS_S_wdc,0.5,3);
SoSOS_q_A_total = sum(SoSOS_q_A,2);
for i=1:n_ESB_gf
    SoSOS_q_A(i,:) = SoSOS_q_A(i,:)/SoSOS_q_A_total(i);     %scaling to 1 for balance 
end
SoSOS_gf(:,:) =SoSOS_q_A(:,:)*sosos_gf2suf;
SoSOS_gf(:,:)=SoSOS_gf(:,:)./sum(SoSOS_gf(:,:),2);%scaling to 1
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

n_ESB=length(boundary);
n_sector=length(sectors);

colormap_A = brewermap(n_sector+6,'Spectral');
colormap_D = brewermap(21,'Spectral');
colormap_F = brewermap(15,'RdBu');
bar_label = cellstr(string([1:1:n_sector]));
d = [1:1:n_ESB];

fig2=figure('Units','centimeters','PaperUnits','centimeters','OuterPosition',[0 0 26 16.5],'PaperSize',[26 16.5]);
%% left figure SoSOS
    %ah=tight_subplot(1,2,0.105,0.04,[0.13 0.038]);
    ax1 = subplot(2,2,[1,3]);
    set(ax1,'fontsize',8, 'fontname', 'Times New Roman')
    axes(ax1);
    hold on
    %%%plotting sufficiency-based SoSOS
    yA   =sosos_basis(1:length(sectors),:)';
    plot_A=barh(d,yA,0.25, 'stacked','FaceColor', 'flat');
    for j=1:n_sector
        set(plot_A(j),'CData',colormap_A(j+3,:));
    end
    %%%%%%%%%%%%%%%%%
    
    %%%plotting grandfathering SoSOS /preliminary & fossil free ecoinvent/
    %
    hold on;
    yA_gf =SoSOS_gf(:,:)';
    for i=1:11
        yA_gf(:,i)=yA_gf(:,i)/sum(yA_gf(:,i));
    end
    yA_gf=yA_gf';
    plot_A2=barh(d-0.3,yA_gf,0.25,'stacked','FaceColor','flat');
    for j=1:n_sector
         set(plot_A2(j),'CData',colormap_A(j+3,:));
    end
    
    hold on;
    yA_ff=sosos_ff(1:length(sectors),:)';
    plot_A3=barh(d+0.3,yA_ff,0.25,'stacked','FaceColor','flat');
    for j=1:n_sector
         set(plot_A3(j),'CData',colormap_A(j+3,:));
    end
    %}
    
    
    %%%%%%%%%%%%%%%%% Base labeling
    
   
    lblpos = yA/2 + cumsum([zeros(size(yA,1),1) yA(:,1:end-1)],2);
    for k1 = 1:size(yA,1)
        for k2 = 1:size(yA,2)
            if yA(k1,k2)>0.025
                text(lblpos(k1,k2), d(k1), bar_label(k2),'FontSize',8,'HorizontalAlignment','center', 'fontname', 'Times New Roman')%-0.25 if two SoSOS
            end
        end
    end
    
    %%%%%%%%%%grandfathering labeling
    %
        lblpos = yA_gf/2 + cumsum([zeros(size(yA_gf,1),1) yA_gf(:,1:end-1)],2);
    for k1 = 1:size(yA_gf,1)
        for k2 = 1:size(yA_gf,2)
            if yA_gf(k1,k2)>0.025
                text(lblpos(k1,k2), d(k1)-0.3, bar_label(k2),'FontSize',8,'HorizontalAlignment','center', 'fontname', 'Times New Roman')%+0.25 if two SoSOS
            end
        end
    end
    %%%%%%%%%%%%%
    
    %%%%%%%%%%fossil free labeling
    lblpos = yA_ff/2 + cumsum([zeros(size(yA_ff,1),1) yA_ff(:,1:end-1)],2);
    for k1 = 1:size(yA_ff,1)
        for k2 = 1:size(yA_ff,2)
            if yA_ff(k1,k2)>0.025
                text(lblpos(k1,k2), d(k1)+0.3, bar_label(k2),'FontSize',8,'HorizontalAlignment','center', 'fontname', 'Times New Roman')%+0.25 if two SoSOS
            end
        end
    end
    text(-0.03, 1.00, 'Base','HorizontalAlignment','right','FontSize',8, 'fontname', 'Times New Roman');
    text(-0.03, 0.67, 'Grandfathering','HorizontalAlignment','right','FontSize',8, 'fontname', 'Times New Roman');
    text(-0.03, 1.33, 'FF LD WB noLT','HorizontalAlignment','right','FontSize',8, 'fontname', 'Times New Roman');
    %}
    %%%%%%%%%%%%%
    
    if turn
        text(1.28*ones(n_ESB,1), d, string(boundary),'HorizontalAlignment','right','FontSize',8, 'fontname', 'Times New Roman', 'Rotation',-45);
    else
        text(1.02*ones(n_ESB,1), d, string(boundary),'HorizontalAlignment','left','FontSize',8, 'fontname', 'Times New Roman');
    end
    
    hold off
    
    ax1.YDir='reverse';
    ax1.XLim=[0 1];
    ax1.YLim=[0.5 n_ESB+0.5];
    ax1.Box='on';
    grid on
    %set(ah(1),'XTick',d,'XTickLabel',0:0.1:1, 'YTickLabel',[])
    set(ax1, 'TickDir', 'out', 'YTick', [0:11]+0.5,'XTick',d,'XTickLabel',0:0.1:1, 'YTickLabel',[]);
    xticks(0:0.1:1)
    %Title_1=title(ah(1),['a) Wirkungsanteile der Ressourcensegmente am sicheren Handlungsspielraum (SoSOS)'],'FontSize',10);
    Title_1=title(ax1,['a)'],'FontSize',10);
    set(Title_1, 'Position',Title_1.Position-[0 0.1 0])
    
    L1=legendflex(join([bar_label' sectors']),'xscale',0.3,'ncol',1,'anchor',[7,5],'buffer',[-0.005,0],'bufferunit','normalized','padding',[1 2 5],'title','Resource segments');
    %set(ah(1),'YTick',[]);
    %L=legend(join([bar_label' sector]));
    %set(L,'Position',[0.01 0.054 0.15 0.3],'Units','normalized','NumColumns',1,'FontSize',8)
    %L.Title.String = 'Ressourcen-Segmente';
    
    %print(fig2,'fig_SoSOS'-png');
    
%% right figure
    %right figure: violinplot of suffiency basket
    pop_2023=8000000000;
    pop_2085=10400000000;
    pop_safe=3000000000;
    
    pop = pop_2085; %Set population size
    
    offset = 1; % 2: CO2 & GWP normal scale, rest lognormal | 1: CO2 normal scale only
    
    scenarios = {...
       'basic';...
       %'basic_LD';...
       %'basic_HD';...
       'ff';...
       %'ff_LD';...
       %'ff_HD';...
       %'basic_wb';...
       %'basic_LD_wb';...
       %'basic_HD_wb';...
       %'ff_wb';...
       %'ff_LD_wb';...
       %'ff_HD_wb';...
       'ff_LD_wb_wo_LUC';...
       %'ff_LD_wo_LUC';...
    };

    show_P_v = 'ff_LD_wb_wo_LUC';
    results_visible = 1;
    
    if results_visible == 0
        disp('Plot visibility are set off. Change to on to see them.')
    end
    
    ESB_limit = quantile(ESB,0.005,3);
    n_runs_ESB=100000;
    n_runs_sp=1000;
    
    filepaths = strings(1,length(scenarios));
    mc_impacts = zeros(n_runs_sp, n_ESB,length(scenarios));
    for i=1:length(scenarios)
        filepath     = append('Monte-Carlo-Sim_dls_basket_', scenarios{i}, '_run.xlsx');
        mc_impacts(:,:,i)= xlsread(filepath);
    end
    
    %load('ESB.mat');
    
%
    P_v = zeros(n_ESB, length(scenarios));
    for i=1:n_ESB
        N_v=zeros(1,length(scenarios)); %number of violations
        for k=1:length(scenarios)
            impact_matrix = mc_impacts(:,:,k)';
            for j=1:n_runs_sp
                if pop*impact_matrix(i,j)>ESB(i,1,j*(n_runs_ESB/n_runs_sp))
                    N_v(k)=N_v(k)+1;
                end
            end
        P_v(i,k) = N_v(k)/n_runs_sp;
        end

    end

    %}

    Y = zeros(n_ESB, n_runs_sp, length(scenarios));
    for k=1:length(scenarios)
        impact_matrix = mc_impacts(:,:,k)';
        for i=1:n_runs_sp
            if impact_matrix(2,i)<0
                impact_matrix(2,i)=10^-10;%cut negative values (GWP) in lognormal scale if less than 1%
            end
        end
        for j=1:n_runs_sp
            y(:,j)  = pop*impact_matrix(:,j)./ESB_limit;
        end
        Y(:,:,k) = y;
    end

    for i=1:n_runs_ESB
        y_ESB (:,i) = ESB(:,1,i)./ESB_limit; % normalized PBs
        y_2011(:,i) = q_A_total(:,1,i)./ESB_limit; % normalized impact 2011
    end

    %axes(ah(2));
    %hold on
    
    names = {...
       'PBs'...
       'pop high'...
       'pop low'...
       '2011'...
       'basic'...
       'basic_LD'...
       'basic_HD'...
       'ff'...
       'ff_LD'...
       'ff_HD'...
       'basic_wb'...
       'basic_LD_wb'...
       'basic_HD_wb'...
       'ff_wb'...
       'ff_LD_wb'...
       'ff_HD_wb'...
       'ff_LD_wb_wo_LUC'...
       'ff_LD_wo_LUC'...
    };
    %                 PBs popH popL 2011 basic LD HD ff ff_LD ff_HD  basic_wb
    colormap_values = [14   15   9    15   2   4  1   6   8   4      11         3    4   17   1   19  17   17];
    which_map       = {'F'  'F' 'F'  'D' 'F'  'D' 'D' 'D' 'D' 'D'     'D'      'D'   'D' 'D' 'F' 'D'  'D'  'D'};
    
    dict = containers.Map(names,colormap_values);
    map  = containers.Map(names,which_map);

    ax2 = subplot(2,2,2); %normal scale
    for k=1:size(Y,3)
        y = Y(:,:,k);
        color = dict(char(scenarios(k)));
        if map(char(scenarios(k)))=='D'
            this_colormap = colormap_D;
        elseif map(char(scenarios(k)))=='F'
            this_colormap = colormap_F;
        end
        V(k)=violinplot(y(1:offset,:)',d,'ViolinColor',this_colormap(color,:),'ShowData', false,'ViolinAlpha',0.5, 'Width',0.3);
        if results_visible ==0
            V(k).ViolinPlot.Visible = 'off';
            V(k).MedianPlot.Visible = 'off';
            V(k).WhiskerPlot.Visible = 'off';
            V(k).MeanPlot.Visible = 'off';
            V(k).ScatterPlot.Visible = 'off';
            %V(k).NotchPlots.Visible = 'off';
            V(k).BoxPlot.Visible = 'off';
        end
    end
    
    color_ESB = dict('PBs');
    color_2011 = dict('2011');
    
    v_ESB = violinplot(y_ESB(1:offset,:)',d,'ViolinColor',colormap_D(color_ESB,:),'ShowData', false,'ViolinAlpha',0.5, 'Width',0.3);
    v_2011= violinplot(y_2011(1:offset,:)',d,'ViolinColor',colormap_F(color_2011,:),'ShowData', false,'ViolinAlpha',0.5, 'Width',0.3);
    
    ax3 = subplot(2,2,4);% lognormal scale
    
    v1 = violinplot(y_ESB(1+offset:11,:)',d,'ViolinColor',colormap_D(color_ESB,:),'ShowData', false,'ViolinAlpha',0.5, 'Width',0.3);
    v2 = violinplot(y_2011(1+offset:11,:)',d,'ViolinColor',colormap_F(color_2011,:),'ShowData', false,'ViolinAlpha',0.5, 'Width',0.3);
    
    for p=1:length(v1)
        v1(p).MedianPlot.Marker ='x';
        v1(p).MedianPlot.SizeData =20;
        v2(p).MedianPlot.Marker ='x';
        v2(p).MedianPlot.SizeData =20;
    end
    
    M = zeros(size(Y,3), 10);
    
    for k=1:size(Y,3)
        y = Y(:,:,k);
        color = dict(char(scenarios(k)));
        if map(char(scenarios(k)))=='D'
            this_colormap = colormap_D;
        elseif map(char(scenarios(k)))=='F'
            this_colormap = colormap_F;
        end
        v = violinplot(y(1+offset:11,:)',d,'ViolinColor',this_colormap(color,:),'ShowData', false,'ViolinAlpha',0.5, 'Width',0.3);
        for p=1:length(v)
            v(p).MedianPlot.Marker ='x';
            v(p).MedianPlot.SizeData =20;
            median(p) = v(p).MedianPlot.YData;
            if results_visible ==0
                v(p).ViolinPlot.Visible = 'off';
                v(p).MedianPlot.Visible = 'off';
                v(p).WhiskerPlot.Visible = 'off';
                v(p).MeanPlot.Visible = 'off';
                v(p).ScatterPlot.Visible = 'off';
                %v(p).NotchPlots.Visible = 'off';
                v(p).BoxPlot.Visible = 'off';
            end
        end
        M(k, :) = median;
    end

    %text(5.8,max(y4(1,:)-0.6),'\leftarrow planetare Grenze','FontSize',8)
    %text(4.9,min(y5(5,:)),'Pop(2020)=7,8 Mil. \rightarrow','HorizontalAlignment','right','FontSize',8)
    %text(4.9,min(y6(5,:))+0.01,'\leftarrow Pop(2050)=9,7 Mil.','HorizontalAlignment','left','FontSize',8)
    axes(ax3);
    line([0 n_ESB+1],[1 1],'Color','red');

    axes(ax2);
    line([0 n_ESB+1],[1 1],'Color','red');
    
    idx = find(all(ismember(scenarios,show_P_v),2)); %index of scenario in scenarios array, where Pv should be shown
    for k=1:n_ESB
        if turn
            t(k) = text(k*1.41-0.31,52,join(['P_v=' string(round(P_v(k, idx),2))]),'FontSize',7, 'fontname', 'Times New Roman', 'Rotation', -45);
        else
            t(k) = text(k*1.31-0.31,52,join(['P_v=' string(round(P_v(k, idx),2))]),'FontSize',7, 'fontname', 'Times New Roman');
        end
    end

    hold off
    ax2.Box='on';
    ax3.Box='on';
    grid on

    ax2.View=[90 90];
    ax2.OuterPosition = [0.5343 0.765+offset*0.0909 0.4097 0.182-offset*0.0909];
    ax2.YAxisLocation = 'right';

    ax3.XLim= [0.5 n_ESB+0.5-offset];
    ax3.YLim= [0.003 50];
    ax3.View=[90 90];
    ax3.OuterPosition = [0.5343 0.013 0.4097 0.8+offset*0.0909];
    
    set(ax2,'XTick',d,'XTickLabel',[],'YTick',[-20 1 10 30 50], 'XLim', [0.5 offset+0.5], 'YLim', [-72 50]);
    set(ax3,'XTick',d,'XTickLabel',[],'YTick',[0.003 0.01 0.05 0.1 0.5 1 5 10 50],'YScale', 'log', 'YGrid', 'on', 'XGrid', 'on');

    %set(ah(2),'XTick',d,'XTickLabel',[],'YTick',[0.002 0.01 0.05 0.1 0.5 1 5 10 50]);

    set(ax2,'fontsize',8, 'fontname', 'Times New Roman');
    set(ax3,'fontsize',8, 'fontname', 'Times New Roman');
    %Title_2=title(ah(2),['b) Wirkung des suffizienten Lebensstandards auf die planetaren Grenzen'],'FontSize',10);
    Title_2=title(ax2,['b)'],'FontSize',10);

    set(Title_2, 'Position',Title_2.Position-[0.2 0 0])
    set(Title_1, 'FontSize',10)
    %set(gcf,'color','w');

    legend_entries={%'Base 8 bn.';...
                    'Base 10.4 bn.';...
                    %'Base 3.6 bn.';...
                    %'LD';...
                    %'HD';...
                    'FF';...
                    %'FF LD';...
                    %'FF HD';...
                    %'PBs';...
                    %'Base 8 bn. WB';...
                    %'Base 10.4 bn. WB';...
                    %'LD WB';...
                    %'HD WB';...
                    %'FF WB';...
                    %'FF LD WB';...
                    %'FF HD WB';...
                    'FF LD WB noLT';...
                    %'FF LD noLT';...
                    'PBs';...
                    'Impact 2011';...
                    };
    %[hl(1).leg, hl(1).obj, hl(1).hout, hl(1).mout]=legendflex(legend_entries,'xscale',0.3,'ncol',1,'anchor',[1,1],'buffer',[0.01 -0.01],'bufferunit','normalized','padding',[1 2 5],'title','scenarios');
    %
    V_colors = zeros(1, length(scenarios)+2);
    for p=1:length(V)
       V_colors(p) = V(p).ViolinPlot;
       V(p).MedianPlot.Marker ='x';
       V(p).MedianPlot.SizeData =20;
    end
     
    V_colors(length(scenarios)+1)=v_ESB.ViolinPlot;
    v_ESB.MedianPlot.Marker ='x';
    v_ESB.MedianPlot.SizeData =20;
    
    V_colors(length(scenarios)+2)=v_2011.ViolinPlot;
    v_2011.MedianPlot.Marker ='x';
    v_2011.MedianPlot.SizeData =20;
    
    h=legend(V_colors,legend_entries,'Location', 'southwest');
    h.ItemTokenSize=[8,10]; h.EdgeColor=[0 0 0];
    
    if turn
        xtickangle(ax2, -90);
        xtickangle(ax3, -90);
        ytickangle(ax2, -90);
        ytickangle(ax3, -90);
        
        h.Visible ='off';
    end
    
    %}
    set(gcf, 'Color', 'w')
    export_fig fig_SJOS_2085.png -m3
    %export_fig result_0.png -m2